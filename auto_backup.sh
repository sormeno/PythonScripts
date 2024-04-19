cd home/filip/PythonScripts/
git add .
#count staged file
count=$(git diff --cached --name-only | wc -l)
if [ "$count" -gt 0 ]; then
    commit_message=$(date +'%Y-%m-%d')
    git commit -m "BACKUP $commit_message"
    git push
fi