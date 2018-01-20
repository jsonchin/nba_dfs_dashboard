# NBA DFS Dashboard

Dashboard and various tools for NBA DFS.

Very temporary instructions:

1) Setup Flask (TODO setup virtualenv)
```
python setup.py
```

2) Setup React (might be some issues with package.json)
```
cd nba_dashboard/static
npm init
npm i webpack --save-dev
npm i babel-core babel-loader babel-preset-es2015 babel-preset-react --save-dev
npm run watch
npm i react react-dom --save-dev
```

3) Run the app (while in the root directory)
```
flask run
```