
db.define_table('modules',
   Field('shortname','string'),
   Field('description','text'),
   Field('pathtofile','string'),
   migrate = 'runestone_modules.table' if settings.migrate else False
)
   
db.define_table('projects',
   Field('projectcode','string'),
   Field('description','string'),
   migrate = 'runestone_projects.table' if settings.migrate else False
)
   