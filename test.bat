curl.exe -s -X POST ^
  -H "Content-Type: application/json" ^
  -d "{\"url\": \"https://www.google.com\"}" ^
  http://127.0.0.1:5000/shorten

curl.exe -s -X POST ^
  -H "Content-Type: application/json" ^
  -d "{\"url\": \"davidchalupa.github.io\"}" ^
  http://127.0.0.1:5000/shorten
