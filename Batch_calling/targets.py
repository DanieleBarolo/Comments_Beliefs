target_list_old = {
    # topic 1
    'Obama',
    'Trump',
    'Democrats',
    'Republicans (GOP)',
    # topic 2
    'Higher taxes',
    'Economic growth',
    'Government spending',
    # topic 4
    'Hillary Clinton',
    'Nancy Pelosi',
    'Sarah Palin',
    # topic 5
    'Black people',
    'White people',
    'Police (cops)',
    # topic 6
    'Muslims',
    'Islam',
    'Terrorism',
    # topic 7
    'God',
    'The church',
    'Jesus',
    'Christians',
    # topic 8
    'Fox News',
    'CNN',
    'MSNBC',
    'Fake news',
    'Breitbart',
    'The press',
    'Journalists',
    # topic 9
    'California',
    'Texas',
    # topic 10
    'FBI',
    'CIA',
    'NSA',
    'Edward Snowden',
    'Mueller',
    # other topics
    'Healthcare',
    'Obamacare',
    'Social welfare',
    'Climate change',
    'Green energy',
    'Fossil fuels'
    'Immigration / immigrants',
    'Mexicans' # to test Tiamo mostly. 
}

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
target_list = { 
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