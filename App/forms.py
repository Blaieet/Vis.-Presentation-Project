from wtforms import Form,FieldList
from wtforms import TextField,FormField
from wtforms.validators import required
from wtforms import PasswordField,StringField,validators,BooleanField,IntegerField, ValidationError, SelectField, FloatField, RadioField


class selectYear(Form):
    year = SelectField('Year',choices=[('8',"2008-09"),('9',"2009-10"),('10',"2010-11"),('11',"2011-12"),
                                        ('12',"2012-13"),('13',"2013-14"),('14',"2014-15"),('15',"2015-16")])

    top = SelectField('Best/Worse', choices=[('top', 'Top 5'), ('bottom', 'Bottom 5')])











