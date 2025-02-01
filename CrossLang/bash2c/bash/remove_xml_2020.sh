#insecure
find . -name "*.txt" -print0 | xargs -0 -l xx sh -c "rm xx"

#secure
find . -regextype sed -regex "./[A-Za-z0-9]*.txt" -print0 | xargs -0 -l sh -c "rm xx"
