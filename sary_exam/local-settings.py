from sary_exam.settings import *

DATABASES = {'default': env.db("LOCAL_DB_URL")}