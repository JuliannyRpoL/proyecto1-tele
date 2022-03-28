NAME=$1$2-tele-eafit

git checkout $1
heroku create $NAME
git remote add heroku-$1$2 https://git.heroku.com/$NAME.git
git push heroku-$1$2 $1:master
