from newsplease import NewsPlease
test_url = "https://thehill.com/homenews/administration/588527-biden-takes-on-trump-in-fiery-address-on-jan-6"
article = NewsPlease.from_url(test_url)
print(article.get_dict()['maintext'])