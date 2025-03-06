import requests
from bs4 import BeautifulSoup
import datetime

# try a Breitbart article 
url = "https://www.breitbart.com/politics/2013/08/13/hyperloop-could-travel-from-la-to-san-francisco-in-30-minutes/"

response = requests.get(url)
if response.status_code == 200:
    html_content = response.text
    # parse this html_content with BeautifulSoup
else:
    print("Error fetching page")

soup = BeautifulSoup(html_content, "html.parser")

# Extract the title:
title = soup.find("h1")
if title:
    article_title = title.get_text(strip=True)

# Extract the article body:
body_div = soup.find("div", class_="entry-content")
if body_div:
    article_body = body_div.get_text(strip=True)

### try more broadly ###
d_links = {}
#d_links['motherjones'] = [
#{'_id': '6562882107', 'dislikes': 0, 'likes': 0, 'clean_title': 'The Government’s Own Watchdog Says Massive Poultry Companies Are Exploiting Small Business Loans', 'createdAt': datetime.datetime(2018, 3, 19, 15, 33, 16), 'isClosed': False, 'link': 'https://www.motherjones.com/food/2018/03/government-watchdog-audit-poultry-small-business-loans-booker-trump-inspector-general-contract-chicken-farmer/', 'forum': 'motherjones', 'posts': 0},
#{'_id': '3889109724', 'clean_title': 'The Terrifying Truth About Air Pollution and Dementia', 'dislikes': 0, 'likes': 0, 'createdAt': datetime.datetime(2015, 6, 29, 13, 2, 5), 'isClosed': False, 'link': 'http://m.motherjones.com/environment/2015/05/air-pollution-dementia-alzheimers-brain?__surl__=Igtxx&__ots__=1435582556655&__step__=1', 'forum': 'motherjones', 'posts': 0},
#{'_id': '3753966078', 'clean_title': "Shelby Lynne's Down-Home Country Music Is the Real Deal", 'dislikes': 0, 'likes': 0, 'createdAt': datetime.datetime(2015, 5, 11, 10, 11, 59), 'isClosed': False, 'link': 'http://www.motherjones.com/node/274916', 'forum': 'motherjones', 'posts': 2},
#{'_id': '780821937', 'clean_title': 'http', 'dislikes': 0, 'likes': 0, 'createdAt': datetime.datetime(2012, 7, 26, 14, 3, 51), 'isClosed': False, 'link': 'http://motherjones.tumblr.com/post/28053223700', 'forum': 'motherjones', 'posts': 0},
#{'_id': '6659113679', 'dislikes': 0, 'likes': 0, 'clean_title': 'Lawmakers Just Might Do Something Positive for Pregnant Women for a Change', 'createdAt': datetime.datetime(2018, 5, 8, 15, 41, 46), 'isClosed': False, 'link': 'http://www.motherjones.com/node/601410', 'forum': 'motherjones', 'posts': 93},
#{'_id': '4467732870', 'clean_title': 'Republicans Are Pushing a Bill That Could Make It Much Harder to Sue Volkswagen', 'dislikes': 0, 'likes': 0, 'createdAt': datetime.datetime(2016, 1, 6, 19, 45, 46), 'isClosed': False, 'link': 'http://www.motherjones.com/environment/2016/01/class-action-republicans-volkswagen-vw-emissions', 'forum': 'motherjones', 'posts': 0},
#{'_id': '6562868765', 'dislikes': 0, 'likes': 0, 'clean_title': 'Laid-Off Coal Workers and Environmentalists Saved This Town', 'createdAt': datetime.datetime(2018, 3, 19, 15, 28, 33), 'isClosed': False, 'link': 'https://www.motherjones.com/environment/2017/07/laid-off-coal-workers-and-enviromentalists-saved-this-town/', 'forum': 'motherjones', 'posts': 0},
#{'_id': '6753531834', 'dislikes': 0, 'likes': 0, 'clean_title': 'In Yelp Style Attack, Trump Slams Red Hen Over Sanders Treatment', 'createdAt': datetime.datetime(2018, 6, 25, 12, 48, 34), 'isClosed': False, 'link': 'https://www.motherjones.com/politics/2018/06/trump-red-hen-sanders-virginia-restaurant-dirty/', 'forum': 'motherjones', 'posts': 0},
#{'_id': '786360397', 'clean_title': 'Can We All Please Stop Whining About the Olympics Being Tape Delayed? Thank You.', 'dislikes': 0, 'likes': 0, 'createdAt': datetime.datetime(2012, 7, 31, 3, 37, 43), 'isClosed': False, 'link': 'http://www.motherjones.com/node/188236', 'forum': 'motherjones', 'posts': 65},
#{'_id': '3887733533', 'clean_title': 'American Dreamer', 'dislikes': 0, 'likes': 0, 'createdAt': datetime.datetime(2015, 6, 28, 23, 56, 46), 'isClosed': False, 'link': 'http://www.motherjones.com/politics/1997/01/american-dreamer?page=1', 'forum': 'motherjones', 'posts': 0},
#]

#d_links['atlantic'] = [
#{'_id': '886591430', 'dislikes': 0, 'likes': 0, 'clean_title': 'Can We Just Vaccinate Our Kids Against HPV Already?', 'createdAt': datetime.datetime(2012, 10, 15, 20, 0, 56), 'isClosed': False, 'link': 'http://theatlantic.feedsportal.com/c/34375/f/625830/s/2480e7ca/l/0L0Stheatlantic0N0Chealth0Carchive0C20A120C10A0Ccan0Ewe0Ejust0Evaccinate0Eall0Ekids0Efor0Ehpv0Ealready0C2636250C/story01.htm', 'forum': 'theatlantic', 'posts': 0},
#{'_id': '7074456422', 'dislikes': 0, 'likes': 0, 'ratingsEnabled': False, 'createdAt': datetime.datetime(2018, 11, 27, 17, 43, 47), 'adsDisabled': False, 'clean_title': "Graphic of the Day: The Cisco 'Artichoke of Attack'", 'isClosed': False, 'link': 'https://www.theatlantic.com/technology/archive/2010/07/graphic-of-the-day-the-cisco-artichoke-of-attack/60464/', 'forum': 'theatlantic', 'posts': 0},
#{'_id': '2048917114', 'dislikes': 0, 'likes': 0, 'clean_title': 'The Wrong Kind of Ethanol Boom', 'createdAt': datetime.datetime(2013, 12, 13, 21, 49, 35), 'isClosed': False, 'link': 'http://theatlantic.feedsportal.com/c/34375/f/625839/s/34cb4cd8/sc/8/l/0L0Stheatlantic0N0Ctechnology0Carchive0C20A130C120Cthe0Ewrong0Ekind0Eof0Eethanol0Eboom0C2823550C/story01.htm', 'forum': 'theatlantic', 'posts': 0},
#{'_id': '2265705782', 'dislikes': 0, 'likes': 0, 'clean_title': 'Dissent Of The Day', 'createdAt': datetime.datetime(2014, 2, 14, 12, 54, 54), 'isClosed': False, 'link': 'http://www.theatlantic.com/daily-dish/archive/2009/02/dissent-of-the-day/205143/', 'forum': 'theatlantic', 'posts': 0},
#{'_id': '571841869', 'dislikes': 0, 'likes': 0, 'clean_title': 'The Anti-Person And Clinton - The Daily Dish', 'createdAt': datetime.datetime(2012, 2, 11, 1, 1, 44), 'isClosed': False, 'link': 'http://www.theatlantic.com/daily-dish/archive/2008/03/the-anti-person-and-clinton/218567/', 'forum': 'theatlantic', 'posts': 0},
#{'_id': '679871565', 'dislikes': 0, 'likes': 0, 'clean_title': 'http', 'createdAt': datetime.datetime(2012, 5, 7, 19, 11, 9), 'isClosed': False, 'link': 'http://theatlantic.tumblr.com/post/22596539173', 'forum': 'theatlantic', 'posts': 0},
#{'_id': '6670326908', 'dislikes': 0, 'likes': 0, 'ratingsEnabled': False, 'createdAt': datetime.datetime(2018, 5, 14, 12, 46, 58), 'adsDisabled': False, 'clean_title': 'Assad Is Desperate for Soldiers', 'isClosed': False, 'link': 'https://www.theatlantic.com/international/archive/2018/05/syria-assad-conscription-refugees-lebanon/560282/', 'forum': 'theatlantic', 'posts': 0},
#{'_id': '573820679', 'dislikes': 0, 'likes': 0, 'clean_title': "Video Shows Syrian Anti-Aircraft Tank Firing Randomly Into Peoples' Homes - Max Fisher - International", 'createdAt': datetime.datetime(2012, 2, 13, 0, 23, 25), 'isClosed': False, 'link': 'http://www.theatlantic.com/international/archive/2012/02/video-shows-syrian-anti-aircraft-tank-firing-randomly-into-peoples-homes/252954/', 'forum': 'theatlantic', 'posts': 0},
#{'_id': '9346032877', 'dislikes': 0, 'likes': 0, 'ratingsEnabled': False, 'createdAt': datetime.datetime(2022, 9, 9, 17, 18, 23), 'adsDisabled': False, 'clean_title': 'How She Did It', 'isClosed': False, 'link': 'https://www.theatlantic.com/ideas/archive/2022/09/queen-elizabeth-death-trump-british-monarchy/671386/?s_o=asc', 'forum': 'theatlantic', 'posts': 0},
#{'_id': '1806499989', 'dislikes': 0, 'likes': 0, 'clean_title': "House GOP: Delay Obamacare or We'll Shut the Government Down", 'createdAt': datetime.datetime(2013, 9, 28, 23, 59, 32), 'isClosed': False, 'link': 'http://theatlantic.feedsportal.com/c/34375/f/625839/s/31d22a89/sc/7/l/0L0Stheatlantic0N0Cpolitics0Carchive0C20A130C0A90Chouse0Egop0Edelay0Eobamacare0Eor0Ewell0Eshut0Ethe0Egovernment0Edown0C280A0A960C/story01.htm', 'forum': 'theatlantic', 'posts': 0},
#]

#d_links['gatewaypundit'] = [
#{'_id': '3621194581', 'dislikes': 0, 'likes': 0, 'ratingsEnabled': False, 'createdAt': datetime.datetime(2015, 3, 24, 1, 32, 51), 'adsDisabled': False, 'clean_title': 'NC State Bans Drinking at Fraternities… Except Black Ones', 'isClosed': False, 'link': 'http://www.thegatewaypundit.com/2015/03/nc-state-bans-drinking-at-fraternities-except-black-fraternities/', 'forum': 'thegatewaypundit', 'posts': 53},
#{'_id': '9326279997', 'dislikes': 0, 'likes': 0, 'ratingsEnabled': True, 'createdAt': datetime.datetime(2022, 8, 27, 3, 37, 30), 'adsDisabled': False, 'clean_title': 'US Marine Says Suicide Bomber Was Spotted at Kabul Airport Before Blast But Military Brass Would Not Let Soldiers Take Him Out — As Reported Earlier: Countdown Given Before Blast', 'isClosed': False, 'link': 'https://www.thegatewaypundit.com/2022/08/us-marine-says-suicide-bomber-spotted-blast-military-brass-not-let-soldiers-take-countdown-given-blast/?ff_source=Email&ff_medium=the-gateway-pundit&ff_campaign=dailypm&ff_content=2022-06-25', 'forum': 'thegatewaypundit', 'posts': 0},
#{'_id': '8525862595', 'dislikes': 0, 'likes': 0, 'ratingsEnabled': False, 'createdAt': datetime.datetime(2021, 5, 17, 23, 27, 27), 'adsDisabled': False, 'clean_title': 'BOOM! CDC Director Finally Admits that COVID Cases are Hugely Over-Counted — Just as Gateway Pundit and Donald Trump Reported in August', 'isClosed': False, 'link': 'https://www.thegatewaypundit.com/2021/05/boom-cdc-director-finally-admits-covid-cases-hugely-counted-just-gateway-pundit-donald-trump-reported-august/?ff_source=TGP%20Communications&ff_medium=email&ff_campaign=9be434f6a0-EMAIL_CAMPAIGN_05_07_2018', 'forum': 'thegatewaypundit', 'posts': 0},
#{'_id': '3499852252', 'dislikes': 0, 'likes': 0, 'ratingsEnabled': False, 'createdAt': datetime.datetime(2015, 2, 9, 16, 22, 29), 'adsDisabled': False, 'clean_title': 'Gallup CEO: I May “Suddenly Disappear” For Telling Truth About Obama Unemployment Rate (Video)', 'isClosed': False, 'link': 'http://www.thegatewaypundit.com/2015/02/gallup-ceo-i-may-suddenly-disappear-for-telling-the-truth-about-obama-unemployment-rate-video/?fb_action_ids=821867334551214&fb_action_types=og.likes&fb_source=other_multiline&action_object_map=%5B787852661262951%5D&action_type_map=%5B%22og.likes%22%5D&action_ref_map=%5B%5D&ModPagespeedFilters=', 'forum': 'thegatewaypundit', 'posts': 0},
#{'_id': '8723504488', 'dislikes': 0, 'likes': 0, 'ratingsEnabled': False, 'createdAt': datetime.datetime(2021, 8, 18, 22, 25, 44), 'adsDisabled': False, 'clean_title': 'Republicans Flips State Senate Seat in District Biden Won by 25 Points in Connecticut Special Election', 'isClosed': False, 'link': 'https://www.thegatewaypundit.com/?p=639375', 'forum': 'thegatewaypundit', 'posts': 0},
#{'_id': '8761077218', 'dislikes': 0, 'likes': 0, 'ratingsEnabled': False, 'createdAt': datetime.datetime(2021, 9, 7, 6, 38, 29), 'adsDisabled': False, 'clean_title': 'Taliban Terrorists Execute Pregnant Female Police Officer In Her Home in Front of Her Family – Use Screwdrivers to Pick Her Brains', 'isClosed': False, 'link': 'https://www.thegatewaypundit.com/2021/09/taliban-terrorists-execute-pregnant-female-police-officer-home-front-family-use-screwdrivers-pick-brains/?__cf_chl_captcha_tk__=pmd_fTtYS81T_yYSmGH8ip3m8_8.aOW4arFi46se4cOGKlM-1630996651-0-gqNtZGzNA7ujcnBszQi9', 'forum': 'thegatewaypundit', 'posts': 0},
#{'_id': '4424171689', 'dislikes': 0, 'likes': 2, 'ratingsEnabled': False, 'createdAt': datetime.datetime(2015, 12, 22, 4, 45, 13), 'adsDisabled': False, 'clean_title': 'Confirmed: American Left Has Resorted to Nazi Brown Shirt Tactics to Take Down Donald Trump', 'isClosed': False, 'link': 'http://www.thegatewaypundit.com/2015/12/confirmed-the-american-left-has-resorted-to-nazi-brown-shirt-tactics-to-take-down-donald-trump/', 'forum': 'thegatewaypundit', 'posts': 77},
#{'_id': '9470603598', 'dislikes': 0, 'likes': 0, 'ratingsEnabled': True, 'createdAt': datetime.datetime(2022, 11, 30, 21, 14, 57), 'adsDisabled': False, 'clean_title': 'FINALLY, FINALLY, FINALLY – National Group Uncovers Real-Time Democrat Election Fraud – HERE’S HOW THEY DID IT', 'isClosed': False, 'link': 'https://www.thegatewaypundit.com/2022/11/finally-finally-finally-election-group-uncovers-fraud/?ff_source=add2any&ff_medium=PostBottomSharingButtons&ff_campaign=websitesharingbuttons', 'forum': 'thegatewaypundit', 'posts': 0},
#{'_id': '9397636030', 'dislikes': 0, 'likes': 0, 'ratingsEnabled': True, 'createdAt': datetime.datetime(2022, 10, 14, 11, 20, 26), 'adsDisabled': False, 'clean_title': 'FBI Was Court Ordered to Turn Over Documents on Seth Rich 14 Days Ago – For Some Reason They Are Refusing the Request… Why Is That?', 'isClosed': False, 'link': 'https://www.thegatewaypundit.com/2022/10/fbi-court-ordered-turn-documents-seth-rich-14-days-ago-reason-refusing-request/?ff_source=Email&ff_medium=the-gateway-pundit&ff_campaign=dailyam&ff_content=2022-08-04', 'forum': 'thegatewaypundit', 'posts': 0},
#{'_id': '9082208412', 'dislikes': 0, 'likes': 0, 'ratingsEnabled': True, 'createdAt': datetime.datetime(2022, 3, 21, 21, 30, 20), 'adsDisabled': False, 'clean_title': 'https://www.thegatewaypundit.com/2021/12/watch-christians-protest-satanic-holiday-display-installed-alongside-nativity-scene-illinois-capitol-video/', 'isClosed': False, 'link': 'https://www.thegatewaypundit.com/2021/12/watch-christians-protest-satanic-holiday-display-installed-alongside-nativity-scene-illinois-capitol-video/', 'forum': 'thegatewaypundit', 'posts': 582},
#]

#d_links['thehill'] = [
#{'_id': '7837334847', 'dislikes': 0, 'likes': 0, 'ratingsEnabled': False, 'createdAt': datetime.datetime(2020, 1, 26, 14, 21, 56), 'adsDisabled': False, 'clean_title': 'Poll: Bernie Sanders holds 9-point lead in New Hampshire: poll', 'isClosed': False, 'link': 'https://thehill.com/homenews/campaign-polls/479955-poll-bernie-sanders-holds-9-point-lead-in-new-hampshire-poll', 'forum': 'thehill-v4', 'posts': 317},
#{'_id': '7937720341', 'dislikes': 0, 'likes': 1, 'ratingsEnabled': False, 'createdAt': datetime.datetime(2020, 3, 27, 20, 19, 55), 'adsDisabled': False, 'clean_title': 'Instacart workers set to strike Monday', 'isClosed': False, 'link': 'https://thehill.com/policy/technology/489912-instacart-workers-set-to-strike-monday', 'forum': 'thehill-v4', 'posts': 75},
#{'_id': '5858358698', 'clean_title': 'Gingrich: The poor ‘get crushed’ by deals like Paris climate accord', 'dislikes': 0, 'likes': 0, 'createdAt': datetime.datetime(2017, 5, 28, 17, 47, 6), 'isClosed': False, 'link': 'http://thehill.com/policy/energy-environment/335491-gingrich-the-poor-get-crushed-by-deals-like-paris-climate-accord', 'forum': 'thehill-v4', 'posts': 519},
#{'_id': '6943766983', 'dislikes': 0, 'likes': 0, 'ratingsEnabled': False, 'createdAt': datetime.datetime(2018, 10, 1, 18, 36, 8), 'adsDisabled': False, 'clean_title': 'More Americans oppose Kavanaugh nomination amid partisan rancor: poll', 'isClosed': False, 'link': 'https://thehill.com/homenews/campaign/409305-more-americans-oppose-kavanaugh-nomination-amid-partisan-rancor-poll', 'forum': 'thehill-v4', 'posts': 515},
#{'_id': '845507207', 'clean_title': 'Lieberman fears for country if Senate Dems get to 60 - The Hill - covering Congress, Politics, Political Campaigns and Capitol Hill', 'dislikes': 0, 'likes': 0, 'createdAt': datetime.datetime(2012, 9, 15, 18, 9, 5), 'isClosed': False, 'link': 'http://thehill.com/homenews/campaign/2006-lieberman-fears-for-country-if-senate-dems-get-to-60', 'forum': 'thehill-v4', 'posts': 0},
#{'_id': '646625508', 'dislikes': 0, 'likes': 0, 'ratingsEnabled': False, 'createdAt': datetime.datetime(2012, 4, 12, 16, 20, 20), 'adsDisabled': False, 'clean_title': 'Obama campaign moves to distance itself from Rosen remarks', 'isClosed': False, 'link': 'http://thehill.com/homenews/campaign/221205-obama-campaign-moves-to-distance-itself-from-rosen-remarks', 'forum': 'thehill-v4', 'posts': 178},
#{'_id': '8530471919', 'dislikes': 0, 'likes': 0, 'ratingsEnabled': False, 'createdAt': datetime.datetime(2021, 5, 18, 23, 18, 59), 'adsDisabled': False, 'clean_title': 'On The Money: Pent-up consumer demand fuels post-pandemic spending spree | Biden, Harris release 2020 tax returns', 'isClosed': False, 'link': 'https://thehill.com/policy/finance/overnights/554234-on-the-money-pent-up-consumer-demand-fuels-post-pandemic-spending', 'forum': 'thehill-v4', 'posts': 23},
#{'_id': '529606943', 'dislikes': 0, 'likes': 0, 'ratingsEnabled': False, 'createdAt': datetime.datetime(2012, 1, 6, 22, 47, 21), 'adsDisabled': False, 'clean_title': 'For Dems in Virginia and New Jersey, victory may come from going negative', 'isClosed': False, 'link': 'http://thehill.com/homenews/campaign/61261-for-dems-in-virginia-and-new-jersey-victory-may-come-from-going-negative', 'forum': 'thehill-v4', 'posts': 6},
#{'_id': '8581596479', 'dislikes': 0, 'likes': 0, 'ratingsEnabled': False, 'createdAt': datetime.datetime(2021, 6, 8, 21, 17, 20), 'adsDisabled': False, 'clean_title': 'Tlaib, Dems slam GOP calls for border oversight to fight opioid crisis', 'isClosed': False, 'link': 'https://thehill.com/policy/healthcare/557424-tlaib-dems-slam-gop-calls-for-border-oversight-to-fight-opioid-crisis', 'forum': 'thehill-v4', 'posts': 538},
#{'_id': '5031662828', 'dislikes': 0, 'likes': 0, 'clean_title': 'Ohio man pleads guilty in plot to attack Capitol', 'createdAt': datetime.datetime(2016, 8, 1, 16, 39, 57), 'isClosed': False, 'link': 'http://thehill.com/blogs/blog-briefing-room/news/289996-ohio-man-pleads-guilty-in-plot-to-attack-capitol', 'forum': 'thehill-v4', 'posts': 17},
#]

d_links['breitbart'] = [
{'_id': '7309967891', 'dislikes': 0, 'likes': 0, 'ratingsEnabled': False, 'clean_title': 'EU leaders open to Brexit delay but demand UK approval', 'createdAt': datetime.datetime(2019, 3, 21, 20, 46, 9), 'isClosed': False, 'link': 'https://www.breitbart.com/news/eu-leaders-open-to-brexit-delay-but-demand-uk-approval/', 'forum': 'breitbartproduction', 'posts': 0},
{'_id': '5358997864', 'clean_title': 'Australia considers charging power generators for pollution', 'dislikes': 0, 'likes': 0, 'createdAt': datetime.datetime(2016, 12, 6, 10, 10, 57), 'isClosed': False, 'link': 'http://www.breitbart.com/news/australia-considers-charging-power-generators-for-pollution/', 'forum': 'breitbartproduction', 'posts': 0},
{'_id': '5286213794', 'clean_title': 'Shell gets permits necessary for oil drilling in Arctic', 'dislikes': 0, 'likes': 0, 'createdAt': datetime.datetime(2016, 11, 7, 18, 19, 33), 'isClosed': False, 'link': 'http://www.breitbart.com/news/shell-gets-permits-necessary-for-oil-drilling-in-arctic/', 'forum': 'breitbartproduction', 'posts': 0},
{'_id': '1728735153', 'dislikes': 0, 'likes': 0, 'ratingsEnabled': False, 'createdAt': datetime.datetime(2013, 9, 7, 23, 5, 53), 'adsDisabled': False, 'clean_title': 'Extreme Fishing: New Zealander Jumps From Helicopter to Tackle Marlin', 'isClosed': False, 'link': 'http://www.breitbart.com/Breitbart-TV/2009/03/12/Extreme-Fishing--New-Zealander-Jumps-From-Helicopter-to-Tackle-Marlin', 'forum': 'breitbartproduction', 'posts': 0},
{'_id': '5883104163', 'clean_title': 'Supreme Court to decide if warrants needed for cellular ‘ping’ data', 'dislikes': 0, 'likes': 8, 'createdAt': datetime.datetime(2017, 6, 5, 19, 46, 26), 'isClosed': False, 'link': 'http://www.breitbart.com/news/supreme-court-to-decide-if-warrants-needed-for-cellular-ping-data/', 'forum': 'breitbartproduction', 'posts': 0},
{'_id': '9195159541', 'dislikes': 0, 'likes': 0, 'ratingsEnabled': False, 'createdAt': datetime.datetime(2022, 5, 30, 17, 24, 12), 'adsDisabled': False, 'clean_title': 'Colombian ‘Trump’ threatens leftist’s presidential ambitions', 'isClosed': False, 'link': 'https://www.breitbart.com/news/colombian-trump-threatens-leftists-presidential-ambitions/', 'forum': 'breitbartproduction', 'posts': 0},
{'_id': '1332705282', 'dislikes': 0, 'likes': 0, 'ratingsEnabled': False, 'createdAt': datetime.datetime(2013, 5, 28, 23, 27, 11), 'adsDisabled': False, 'clean_title': 'Tornado watch issued for US Midwest states', 'isClosed': False, 'link': 'http://www.breitbart.com/system/wire/CNG---573dcf3aaf27f411b9358d33944d20cf---461', 'forum': 'breitbartproduction', 'posts': 0},
{'_id': '7024398244', 'dislikes': 0, 'likes': 0, 'clean_title': 'Marseille building collapse death toll rises to four', 'createdAt': datetime.datetime(2018, 11, 6, 19, 40, 4), 'isClosed': False, 'link': 'https://www.breitbart.com/news/marseille-building-collapse-death-toll-rises-to-four/', 'forum': 'breitbartproduction', 'posts': 0},
{'_id': '5613692502', 'clean_title': 'International Women’s Strike Message: ‘Decolonize Palestine,’ Stand Up to ‘White Supremacists’ In Trump Administration', 'dislikes': 0, 'likes': 48, 'createdAt': datetime.datetime(2017, 3, 8, 14, 37, 45), 'isClosed': False, 'link': 'http://www.breitbart.com/jerusalem/2017/03/08/international-womens-strike-message-decolonize-palestine-stand-up-to-white-supremacists-in-u-s-administration/', 'forum': 'breitbartproduction', 'posts': 1254},
{'_id': '9561624851', 'dislikes': 0, 'likes': 0, 'ratingsEnabled': False, 'createdAt': datetime.datetime(2023, 2, 2, 23, 8, 41), 'adsDisabled': False, 'clean_title': 'FACT CHECK: Gavin Newsom Says ‘Permitless Carry Does Not Make You Safer’', 'isClosed': False, 'link': 'https://www.breitbart.com/politics/2023/02/01/fact-check-gavin-newsom-says-permitless-carry-does-not-make-you-safer/', 'forum': 'breitbartproduction', 'posts': 0},
]

# create something more useful
import time
import requests
from bs4 import BeautifulSoup

def retrieve_body(url):
    article_title = ''
    article_body = ''
    
    max_retries = 3             # how many times to retry on 429
    default_sleep_time = 30     # how many seconds to wait if no Retry-After is given

    for attempt in range(max_retries):
        response = requests.get(url)
        
        if response.status_code == 200:
            # good to parse
            break
        elif response.status_code == 429:
            # Too Many Requests
            print(f"429 received. Attempt {attempt+1}/{max_retries} - waiting before retrying.")
            # If the server sent a Retry-After header, use it; otherwise wait default_sleep_time.
            retry_after = response.headers.get("Retry-After")
            if retry_after is not None:
                try:
                    wait_seconds = int(retry_after)
                except ValueError:
                    wait_seconds = default_sleep_time
            else:
                wait_seconds = default_sleep_time
            
            time.sleep(wait_seconds)
        else:
            # Some other HTTP error: we can either break or raise an exception
            print(f"Error fetching {url}: status {response.status_code}")
            return article_title, article_body
    else:
        # If we exit the for-loop normally, it means we never got a 200
        print("Max retries hit, giving up.")
        return article_title, article_body

    # At this point, if we're here, we got a 200 response
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract the title:
    title = soup.find("h1")
    if title:
        article_title = title.get_text(strip=True)

    # Extract the article body:
    body_div = soup.find("div", class_="entry-content")
    if body_div:
        article_body = body_div.get_text(strip=True)
    
    return article_title, article_body
    
results = []
for platform, list in d_links.items():
    print(platform)
    for dictionary in list: 
        id = dictionary['_id']
        print(id)
        clean_title = dictionary['clean_title']
        url = dictionary['link']
        url_title, url_body = retrieve_body(url)
        results.append([platform, id, url, clean_title, url_title, url_body])

import pandas as pd 
pd.set_option('display.max_colwidth', None)
df_results = pd.DataFrame(results, columns=['platform', 'id', 'url', 'clean_title', 'url_title', 'url_body'])
df_results

# test this one 
url = 'https://www.breitbart.com/news/colombian-trump-threatens-leftists-presidential-ambitions/'
response = requests.get(url)
if response.status_code == 200:
    html_content = response.text
    # parse this html_content with BeautifulSoup
else:
    print("Error fetching page")

soup = BeautifulSoup(html_content, "html.parser")

# Extract the title:
title = soup.find("h1")
if title:
    article_title = title.get_text(strip=True)

# Extract the article body:
body_div = soup.find("div", class_="entry-content")
if body_div:
    article_body = body_div.get_text(strip=True)
