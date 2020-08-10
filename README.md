# SpeciesCuration
**更新日期：2020-08-08**
NCBI的taxonomy数据库是目前最常用的物种分类数据库，大多数情况下足够使用。但是当涉及到进化等对分类有着较高要求的时候，taxonomy数据库就力有不殆了，故记录下目前常用的一些资源。

## 有关资源
### taxonkit和taxonomy数据库
Taxonomy作为最常用的数据库，批量查询是一个最基本的需求。这里推荐爪哥的[taxonkit](https://github.com/shenwei356/taxonkit), GO写的，速度很快。而且好用。taxonkit依赖taxonomy数据库的taxdump文件([下载地址](ftp://ftp.ncbi.nih.gov/pub/taxonomy/))

### 多识百科
多识百科是一个中文的、非官方的植物分类网站。目前整合了APG IV和一些其他的信息。优点是在属及属以上的层次已经囊括了最新的主流分类系统，尤其是对一些有争议的地方有相关说明，而且是中文的，用起来方便。缺点是没有精确到种的信息。建议使用多识校正科、属异名。使用[spider_duoshi.py](spider_duoshi.py)可以爬取相关的科、属信息。

### The plant list
[The Plant List](http://www.theplantlist.org/) (TPL)是 世界在线植物志[World Flora Online](http://www.worldfloraonline.org/)
的一个项目。之前作为权威标准也使用了很多年，相关的R包也有。缺点是更新停留在2013年，目前显得有些过时。使用[spider_tpl.py](spider_tpl.py)可以根据异名爬取正名

### species2000
[物种2000](www.catalogueoflife.org)是一个在英国注册的非营利组织，由52个全球性的生物多样性数据库组织以联邦的形式联合而成。优点是每年都会更新数据，而且有[中国节点](http://col.especies.cn/)，并且提供的查询方法十分多样，包括在线网页查询、API查询、离线数据库查询。中国物种名录2000甚至有离线软件（嗯，他们自己写了个软件。。。。）**需要注意的是中国物种名录2000和species2000里面的数据不完全一样，他们又有各自的离线数据库、API**。

#### species2000  
**API：** http://www.catalogueoflife.org/content/web-services  
**离线数据：** http://www.catalogueoflife.org/content/annual-checklist-archive  
**软件：** http://col.especies.cn/download

####中国物种名录2000
都是中文的，自己去看吧

[query_species2000_2.py](query_species2000_2.py)可以使用下载到本地的数据库文件批量查询物种正名。所依赖的数据库文件是上述[离线数据](http://www.catalogueoflife.org/content/annual-checklist-archive)下载的Annual Checklist as Darwin Core Archive解压后的taxa.txt
*ps:* 该文件比较大，内存小于16G不建议使用该脚本，速度也有点感人，查询几千个的话可能需要几十分钟。species2000有个在线的[批量查询功能](http://www.catalogueoflife.org/listmatching/) 但是我估计结果取回速度会更感人，而且结果应该还是要自己解析。  

[query_species2000.py](query_species2000.py)是上述脚本的MySQL版本，优点是对内存要求小（毕竟用的数据库），缺点是速度慢，一个query经实验大概需要5~10s（数据库文件存储于SATA SSD）。适合小批量查询（但是话又说回来了，小批量为什么不直接用API呢？回头可能会写个API的脚本）

[api_sp2000_CN.py](api_sp2000_CN.py)可以使用中国物种名录2000的API进行查询（需注册账号），一天有2000个查询额度（实际上好像目前没有限制，估计是用的人不多）


## 说明
1. 科、属建议以多识为主，主要校正是否有不合法异名（目前来看基本不存在这种情况）;种名建议以species2000为主。多个数据库之间有冲突的时候需要结合实际情况判断，比如使用习惯（比如有时候国内和国外在使用广义属/狭义属上的习惯不一样,例如国际习惯用广义木兰属，但是国内可能习惯用狭义的）等等。
2. 上述所有数据库对藻类的支持都不好，故所有脚本目前不包括藻类校正。
3. 做药用植物校正推荐用中国物种名录2000而不用国际版species2000。原因是：1.国际版特别喜欢用广义属，中国的使用习惯很多时候倾向于狭义属，2.很多国内中药是栽培种、变种，国际版往往不承认这些是独立种，但是目前实际使用中又往往认为他们是独立种。因此使用中国物种名录2000可能更适合药用植物的情况。
4. 非药用植物建议使用国际版species2000。原因是中国物种名录2000对非中国原产的植物支持太差了，10个里面不一定能查到2个。（大部分药用植物是中国原产的）。