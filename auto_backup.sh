git add .
#create commit and push only if there are files staged
count=$(git diff --cached --name-only | wc -l)
if [ "$count" -gt 0 ]; then
    commit_message=$(date +'%Y-%m-%d %H:%M:%S')
    git commit -m "BACKUP $commit_message"
    git push
fi