import core
import model
import settings

def get_communitylist():
	res = []
	for community in model.Community.select().where(model.Community.onsale>0):
		res.append(community.title)
	return res

if __name__=="__main__":
    regionlist = settings.REGIONLIST # only pinyin support
    model.database_init()
    core.GetCommunityByRegionlist(regionlist) # Init,scrapy celllist and insert database; could run only 1st time
    communitylist = get_communitylist() # Read celllist from database
    core.GetHouseByCommunitylist(communitylist)
    core.GetRentByCommunitylist(communitylist)
    core.GetSellByCommunitylist(communitylist)
