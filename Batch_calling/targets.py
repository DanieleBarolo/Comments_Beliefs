

### new draft of targets ### 

# agree / disagree / (neutral)
'''
target_list_tuple = {
    ('Barack Obama', 'I support Barack Obama'),
    ('Donald Trump', 'I support Donald Trump'),
    ('Democrats', 'I support Democrats'),
    ('Republicans (GOP)', 'I support Republicans (GOP)'),
    ('Taxes', 'Taxes are fair'), # maybe good.
    ('The economy', 'The economy is good'), # working well? 
    ('Jobs', 'Good jobs are available'), # ...  
    ('Government', ''),
    ('Hillary Clinton', 'I support Hillary Clinton'),
    ('Nancy Peolosi', 'I support Nancy Pelosi'),
    ('Sarah Palin', 'I support Sarah Palin'),
    ('Black people', '...'),
    ('White people', '...'),
    ('Muslims', 'I like Muslims'),
    ('Islam'),
    ('Terrorism')
}
'''

# tell the model: 
# Favor/Against or Agree/Disagree
target_list_old = { 
    # politics (several topics in the topic model)
    'Barack Obama', 
    'Donald Trump', 
    'Democrats',
    'Republicans (GOP)',
    'Joe Biden',
    'Hillary Clinton',
    'Nancy Pelosi',
    'Sarah Palin',
    'Kamala Harris'
    # economy and jobs
    'Taxes are fair', 
    'The economy is good', 
    'Jobs are available', 
    'Government spending', # consider. 
    # race, crime, religion, immigration
    'Black people',
    'White people',
    'The police (cops)',
    'Crime'
    'Muslims',
    'Islam',
    'Terrorism',
    'Jesus', # God, Bible.
    'Christians',
    'Immigration / immigrants',
    # Media 
    'Fox News',
    'Mainstream / liberal media', # maybe explain e.g., CNN
    'Right-wing media', # maybe explain?
    'Journalists and the press',
    'Social media',
    # other topics
    'Healthcare / Medicare',
    'Social welfare',
    # Elites 
    'Politicians',
    'Science / Scientists',
    'Elites', # requires abstraction: very tricky. 
    # Ideology 
    'Socialism / Communism',
    'Capitalism / Liberalism',
    'Fascism / Nazism',
    # Various inflammatory topics 
    'Vaccines',
    'Covid',
    'Drugs',
    'Abortion',
    'Climate change is a problem', 
    'Climate change is real', 
    'Fossil fuels', 
    'Vegetarians / Vegans',
    # Culture wars 
    'Diversity (DEI)', 
    'Feminism',
    'Woke',
    'Gay / LGTBQ+',
    # Controls 
    'Movies',
    'Sport',
    'Food',
    'Animals', # ...
    'Music',
    # Education
    'We have good schools', # (system)
    'We have good teachers',
    # Geo-politics
    'China',
    'Russia',
    'Israel',
    'Jews',
    'Ukraine'
}

target_list = {
    # politics (several topics in the topic model)
    'Barack Obama', 
    'Donald Trump', 
    'Joe Biden',
    'Democrats',
    'Republicans (GOP)',
    'Liberals',
    'Conservatives',
    'Progressives',
    'Hillary Clinton',
    'Nancy Pelosi',
    'Sarah Palin',
    'Kamala Harris',
    # economy and jobs
    'Taxes are (good | fair)', 
    'Economy is good', 
    'Jobs are (available | good)', 
    'The government', # spending
    # race, crime, religion, immigration
    'Black people',
    'White people',
    'Police',
    'Military',
    'Crime',
    'Muslims',
    'Islam',
    'Terrorism',
    'Christians',
    'Christianity',
    'Immigration / immigrants',
    # Media 
    'Media', # maybe explain e.g., CNN
    'Journalists', # maybe explain?
    'Social media',
    # other topics
    'Healthcare',
    'Social welfare',
    # Elites 
    'Politicians',
    'Scientists',
    'Elites', # requires abstraction: very tricky. 
    # Ideology 
    'Socialism / Communism',
    'Capitalism',
    'Fascism / Nazism',
    # Various inflammatory topics 
    'Vaccines',
    'Covid',
    'Drugs',
    'Abortion',
    'Climate change is (real | a problem)', 
    'Fossil fuels', 
    'Vegetarians / Vegans',
    # Culture wars 
    'Diversity', 
    'Feminism',
    'Woke',
    'Gay / LGTBQ+',
    # Controls 
    'Hobbies',
    'Movies',
    'Sport',
    'Food',
    'Music', 
    # Education
    # 'We have good schools', # (system)
    # 'We have good teachers',
    # Geo-politics
    'China',
    'Russia',
    'Israel',
    'Jews',
    'Ukraine',
    'America / USA',
}
