# Proposed GitHub issues

Draft issue bodies for [Ezra-Black/EB-Flow](https://github.com/Ezra-Black/EB-Flow).

`gh` was not authenticated in the environment that prepared these files. To publish:

```bash
gh auth login

for f in docs/proposed-issues/0*.md; do
  title=$(python3 -c "import re,pathlib; t=pathlib.Path('$f').read_text(); print(re.search(r'title:\\s*\\\"([^\\\"]+)\\\"', t).group(1))")
  labels=$(python3 -c "import re,pathlib; t=pathlib.Path('$f').read_text(); m=re.search(r'labels:\\s*\\[(.*?)\\]', t); print(','.join(re.findall(r'\\\"([^\\\"]+)\\\"', m.group(1)) if m else ''))")
  body_file=$(mktemp)
  # strip YAML front matter
  awk 'BEGIN{p=0} /^---$/{p++; next} p>=2{print}' "$f" > "$body_file"
  if [ -n "$labels" ]; then
    gh issue create --repo Ezra-Black/EB-Flow --title "$title" --label "$labels" --body-file "$body_file"
  else
    gh issue create --repo Ezra-Black/EB-Flow --title "$title" --body-file "$body_file"
  fi
  rm -f "$body_file"
done
```

Or create each issue manually from the markdown files in this folder.
