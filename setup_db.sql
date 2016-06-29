CREATE USER 'quizapp'@'localhost' IDENTIFIED BY 'foobar';
CREATE DATABASE quizapp;
GRANT ALL ON quizapp.* TO 'quizapp'@'localhost';
