#!/usr/bin/env bash

set -euo pipefail

YAML_FILE="papers.yml"
DOWNLOAD_DIR="papers"
PARALLELISM=6

if ! command -v yq &>/dev/null; then
    echo "❌ Python yq (wrapper for jq) not found. Install via 'pip install yq'."
    exit 1
fi

if ! command -v jq &>/dev/null; then
    echo "❌ 'jq' is required but not installed. Install with your package manager."
    exit 1
fi

mkdir -p "$DOWNLOAD_DIR"
TMP_LIST=$(mktemp)
INDEX_LIST=$(mktemp)
FAILED_LIST=$(mktemp)
trap 'rm -f "$TMP_LIST" "$INDEX_LIST" "$FAILED_LIST"' EXIT

slugify() {
    echo "$1" | tr ' /:' '_' | tr -cd '[:alnum:]_'
}

download_one() {
    log() {
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    }

    IFS='|' read -r title link topic <<<"$1"
    [[ -z "$link" || -z "$title" ]] && return

    safe_title=$(slugify "$title")
    safe_topic=$(slugify "$topic")
    topic_dir="$DOWNLOAD_DIR/$safe_topic"
    mkdir -p "$topic_dir"
    filepath="$topic_dir/$safe_title.pdf"

    if [[ -f "$filepath" ]]; then
        log "✅ Already exists: $title"
        return
    fi

    log "⬇️  Downloading: $title"

    curl_common_args=(
        -sSL --fail
        -A "Mozilla/5.0 (Windows NT 10.0; rv:112.0) Gecko/20100101 Firefox/112.0"
        -H "Accept: application/pdf"
    )

    [[ -f cookies.txt ]] && curl_common_args+=(-b cookies.txt)

    # 1st attempt with original referer
    if curl "${curl_common_args[@]}" -e "$link" "$link" -o "$filepath"; then
        log "✅ Downloaded: $title"
        echo "$safe_topic|$safe_title|$title" >>"$INDEX_LIST"
        return
    fi

    log "⚠️  Primary curl attempt failed: $title"

    # 2nd attempt with fallback referer
    if curl "${curl_common_args[@]}" -e "https://www.google.com" "$link" -o "$filepath"; then
        log "✅ Downloaded with fallback referer: $title"
        echo "$safe_topic|$safe_title|$title" >>"$INDEX_LIST"
        return
    fi

    log "⚠️  Curl fallback failed: $title. Trying wget..."

    # 3rd attempt with wget as fallback
    wget_args=(
        --quiet
        --header="User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:112.0) Gecko/20100101 Firefox/112.0"
        --header="Accept: application/pdf"
        --header="Referer: https://dl.acm.org/"
        -O "$filepath"
        "$link"
    )

    if wget "${wget_args[@]}"; then
        log "✅ Downloaded via wget: $title"
        echo "$safe_topic|$safe_title|$title" >>"$INDEX_LIST"
        return
    fi

    log "❌ All attempts failed: $title"
    echo "$safe_topic|$safe_title|$title|$link" >>"$FAILED_LIST"
}

export -f slugify
export -f download_one
export DOWNLOAD_DIR
export INDEX_LIST
export FAILED_LIST

echo "📚 Indexing papers..."

declare -A seen_links

yq . "$YAML_FILE" | jq -c '.[]' | while read -r paper; do
    base_title=$(echo "$paper" | jq -r '.title')
    base_link=$(echo "$paper" | jq -r '.link')
    mapfile -t base_topics < <(echo "$paper" | jq -r '.topics[]')
    topic="${base_topics[0]}"

    if [[ -z "${seen_links["$base_link"]+x}" ]]; then
        printf "%s|%s|%s\0" "$base_title" "$base_link" "$topic" >>"$TMP_LIST"
        seen_links["$base_link"]=1
    fi

    echo "$paper" | jq -c '.related[]?' 2>/dev/null | while read -r related; do
        r_title=$(echo "$related" | jq -r '.title')
        r_link=$(echo "$related" | jq -r '.link')
        if [[ -z "${seen_links["$r_link"]+x}" ]]; then
            printf "%s|%s|%s\0" "$r_title" "$r_link" "$topic" >>"$TMP_LIST"
            seen_links["$r_link"]=1
        fi
    done
done

total=$(tr -cd '\0' <"$TMP_LIST" | wc -c)
echo "🚀 Starting parallel download of $total papers using $PARALLELISM workers..."

xargs -0 -P "$PARALLELISM" -I{} bash -c 'download_one "$@"' _ {} <"$TMP_LIST"

# Markdown index for successful downloads
INDEX_FILE="$DOWNLOAD_DIR/index.md"
echo -e "# Downloaded Papers\n" >"$INDEX_FILE"

sort "$INDEX_LIST" | awk -F'|' '
BEGIN { current_topic = ""; }
{
    topic = $1;
    filename = $2;
    title = $3;
    if (topic != current_topic) {
        if (current_topic != "") print "";
        print "## " topic "\n";
        current_topic = topic;
    }
    print "- [" title "](" topic "/" filename ".pdf)";
}
' >>"$INDEX_FILE"

echo "📘 Markdown index created: $INDEX_FILE"

# Markdown for failed downloads
FAILED_FILE="$DOWNLOAD_DIR/failed.md"
echo -e "# Failed Downloads (manual)\n" >"$FAILED_FILE"

sort "$FAILED_LIST" | awk -F'|' '
{
    topic = $1;
    filename = $2;
    title = $3;
    url = $4;
    print "- **" title "**  \n  → Category: `" topic "`  \n  → URL: [" url "](" url ")\n";
}
' >>"$FAILED_FILE"

echo "🛑 Failed download list created: $FAILED_FILE"
