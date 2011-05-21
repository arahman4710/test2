
var SmartList=Class.create();SmartList.prototype={currentPage:1,currentFlag:"dd1-all",currentFlag2:"dd2-all",options:{},flagInfo:null,listItems:[],itemFlagIndexes:[],hasSecondPagination:false,hasNumResults:false,hasSecondDropdown:false,initialize:function(){var options=Object.extend({baseName:"sl",itemClass:"item",showFlagCount:true,itemFlagClass:"flags",itemFlagSeparator:", ",itemChangeEffect:"Blind",itemChangeDuration:1,pageChangeEffect:"FadeAppear",pageChangeDuration:0.5,numItemsPerPage:10,paginationLeft:"\u00ab",paginationRight:"\u00bb",maxPaginationLinks:10,defaultDropdownOptText:"All items",defaultDropdown2OptText:"All items",dd2Flags:[],optgroups:{}},arguments[0]||{});var listItems=$$("#"+options.baseName+" ."+options.itemClass);var itemFlagIndexes=[];var flagInfo=new Hash();if($(options.baseName+"-flag-dropdown2"))
this.hasSecondDropdown=true;var currFlagIndex=0;for(var i=0;i<listItems.length;i++)
{listItems[i].style.display=(i<options.numItemsPerPage)?"block":"none";var itemFlagNodes=$(listItems[i]).select("."+options.itemFlagClass);var currItemFlagIndexes=[];var linkNodes=[];for(var j=0;j<itemFlagNodes.length;j++)
{var currItemFlagStrings=$(itemFlagNodes[j]).innerHTML.split(/\s+/);var flagSpan=document.createElement("span");for(var k=0;k<currItemFlagStrings.length;k++)
{var currFlag=currItemFlagStrings[k].replace(/&nbsp;/g," ");var ddNum=(this.hasSecondDropdown&&options.dd2Flags.include(currFlag))?2:1;flagIndex=currFlagIndex;if(flagInfo.get(currFlag)==undefined)
{flagInfo.set(currFlag,[currFlagIndex,1,ddNum]);currFlagIndex++;}
else
{var oldFlagInfo=flagInfo.get(currFlag);flagIndex=oldFlagInfo[0];flagCount=oldFlagInfo[1]+1;flagInfo.set(currFlag,[flagIndex,flagCount,ddNum]);}
var a=$(document.createElement("a"));a.setAttribute("href","#");a.addClassName(options.baseName+"-flag"+flagIndex);a.appendChild(document.createTextNode(currFlag));flagSpan.appendChild(a);flagSpan.appendChild(document.createTextNode(options.itemFlagSeparator));currItemFlagIndexes.push(flagIndex);}
$(itemFlagNodes[j]).innerHTML="";$(itemFlagNodes[j]).appendChild(flagSpan);}
if(flagSpan.childNodes.length)
flagSpan.removeChild(flagSpan.childNodes[flagSpan.childNodes.length-1]);itemFlagIndexes[i]=currItemFlagIndexes;}
var sorted=flagInfo.keys().sort();var sortedFlagInfo=new Hash();for(var i=0;i<sorted.length;i++)
{var value=flagInfo.get(sorted[i]);sortedFlagInfo.set(sorted[i],value);}
if($(options.baseName+"-pagination2"))
this.hasSecondPagination=true;if($(options.baseName+"-num-results"))
{this.hasNumResults=true;$(options.baseName+"-num-results").innerHTML=listItems.length;}
this.options=options;this.flagInfo=sortedFlagInfo;this.listItems=listItems;this.itemFlagIndexes=itemFlagIndexes;this.createPagination("dd1-all");this.addDropdowns();$(options.baseName).show();},createPagination:function()
{this._createPaginationGroup("pagination");if(this.hasSecondPagination)
this._createPaginationGroup("pagination2");},showAll:function()
{this.currentFlag="dd1-all";this.currentFlag2="dd2-all";this.filterByFlag(null,"dd1-all");if(this.hasSecondDropdown)
this._selectDropdownOption("dd2-all",2);},addDropdowns:function()
{var options=this.options;var flagInfo=this.flagInfo;var hasSecondDropdown=this.hasSecondDropdown;var currSmartList=this;var s=document.createElement("select");s.onchange=this.filterByFlag.bindAsEventListener(this);var defaultOpt=document.createElement("option");defaultOpt.setAttribute("value","dd1-all");defaultOpt.appendChild(document.createTextNode(options.defaultDropdownOptText));s.appendChild(defaultOpt);flagInfo.each(function(pair){var flag=pair.key;var index=pair.value[0];var count=pair.value[1];var ddNum=pair.value[2];if(ddNum==1)
{var opt=document.createElement("option");opt.setAttribute("value",index);var displayText=(options.showFlagCount)?flag+" ("+count+")":flag;opt.appendChild(document.createTextNode(displayText));s.appendChild(opt);}
$$("."+options.baseName+"-flag"+index).invoke('observe','click',currSmartList.filterByFlag.bindAsEventListener(currSmartList,index));});$(options.baseName+"-flag-dropdown").appendChild(s);if(hasSecondDropdown)
{var s=document.createElement("select");s.onchange=this.filterByFlag.bindAsEventListener(this);var defaultOpt=document.createElement("option");defaultOpt.setAttribute("value","dd2-all");defaultOpt.appendChild(document.createTextNode(options.defaultDropdown2OptText));s.appendChild(defaultOpt);flagInfo.each(function(pair){var flag=pair.key;var index=pair.value[0];var count=pair.value[1];var ddNum=pair.value[2];if(ddNum==2)
{var opt=document.createElement("option");opt.setAttribute("value",index);var displayText=(options.showFlagCount)?flag+" ("+count+")":flag;opt.appendChild(document.createTextNode(displayText));s.appendChild(opt);}});$(options.baseName+"-flag-dropdown2").appendChild(s);}},filterByFlag:function(event,index){var flagIndex=index;if(event!=null&&Event.element(event).value!=undefined)
flagIndex=Event.element(event).value;if(event!=null)
Event.stop(event);var ddNum=this._getFlagDropdownNum(flagIndex);if(ddNum==1)
this.currentFlag=flagIndex;else
this.currentFlag2=flagIndex;var listItems=this.listItems;var options=this.options;var itemFlagIndexes=this.itemFlagIndexes;var count=0;for(var i=0;i<listItems.length;i++)
{if(count>=options.numItemsPerPage)
{listItems[i].hide();continue;}
if(this._shouldDisplayItem(itemFlagIndexes[i]))
{if(listItems[i].style.display=="none")
{switch(options.itemChangeEffect)
{case"Blind":Effect.BlindDown(listItems[i],{duration:options.itemChangeDuration});break;case"FadeAppear":Effect.Appear(listItems[i],{duration:options.itemChangeDuration});break;case"ShrinkGrow":Effect.Grow(listItems[i],{duration:options.itemChangeDuration});break;default:listItems[i].show();break;}}
count++;}
else
{if(listItems[i].style.display!="none")
{switch(options.itemChangeEffect)
{case"Blind":Effect.BlindUp(listItems[i],{duration:options.itemChangeDuration});break;case"FadeAppear":Effect.Fade(listItems[i],{duration:options.itemChangeDuration});break;case"ShrinkGrow":Effect.Shrink(listItems[i],{duration:options.itemChangeDuration});break;default:listItems[i].hide();break;}}
else
listItems[i].hide();}}
if(this.hasNumResults)
{var numResults=this._getNumItemsByFlag();$(options.baseName+"-num-results").innerHTML=numResults;if(numResults==0)
{if($(options.baseName+"-no-results").style.display=="none"||$(options.baseName+"-no-results").style.display=="")
{Effect.Appear($(options.baseName+"-no-results"),{duration:options.itemChangeDuration,delay:options.itemChangeDuration});}}
else
{if($(options.baseName+"-no-results").style.display=="block"||$(options.baseName+"-no-results").style.display=="")
Effect.Fade($(options.baseName+"-no-results"),{duration:options.itemChangeDuration});}}
this._selectDropdownOption(flagIndex,ddNum);this.createPagination(flagIndex);this.currentPage=1;},changePage:function(event,page){var options=this.options;var currentPage=this.currentPage;if(page==currentPage)
return;if(page=="next")
page=currentPage+1;else if(page=="previous")
page=currentPage-1;var selectedFlagItems=this._getItemsByFlag();this._updatePaginationGroup("pagination",selectedFlagItems,page);if(this.hasSecondPagination)
this._updatePaginationGroup("pagination2",selectedFlagItems,page);if(this.hasNumResults)
$(options.baseName+"-num-results").innerHTML=selectedFlagItems.length;var firstItemToHide=(currentPage-1)*options.numItemsPerPage;var maxLastItem=firstItemToHide+options.numItemsPerPage;var lastItemToHide=(maxLastItem>selectedFlagItems.length)?selectedFlagItems.length:maxLastItem;var firstItemToShow=(page-1)*options.numItemsPerPage;var maxLastItem=firstItemToShow+options.numItemsPerPage;var lastItemToShow=(maxLastItem>selectedFlagItems.length)?selectedFlagItems.length:maxLastItem;for(var i=0;i<selectedFlagItems.length;i++)
{if(i>=firstItemToHide&&i<lastItemToHide)
{switch(options.pageChangeEffect)
{case"Blind":Effect.BlindUp(selectedFlagItems[i],{duration:options.pageChangeDuration});break;case"FadeAppear":Effect.Fade(selectedFlagItems[i],{duration:options.pageChangeDuration});break;case"ShrinkGrow":Effect.Shrink(selectedFlagItems[i],{duration:options.pageChangeDuration});break;default:$(selectedFlagItems[i]).hide();break;}}
if(i>=firstItemToShow&&i<lastItemToShow)
{switch(options.pageChangeEffect)
{case"Blind":Effect.BlindDown(selectedFlagItems[i],{delay:options.pageChangeDuration,duration:options.pageChangeDuration});break;case"FadeAppear":Effect.Appear(selectedFlagItems[i],{delay:options.pageChangeDuration,duration:options.pageChangeDuration});break;case"ShrinkGrow":Effect.Grow(selectedFlagItems[i],{delay:options.pageChangeDuration,duration:options.pageChangeDuration});break;default:$(selectedFlagItems[i]).show();break;}}}
this.currentPage=page;Event.stop(event);},_createPaginationGroup:function(cssLabel)
{var listItems=this.listItems;var options=this.options;var flagInfo=this.flagInfo;var flagCount=this._getNumItemsByFlag();var numPages=Math.ceil(flagCount/options.numItemsPerPage);$(options.baseName+"-"+cssLabel).innerHTML="";if(numPages<=1)
return;var pagination=document.createElement("span");var previousSpan=document.createElement("span");previousSpan.setAttribute("id",options.baseName+"-"+cssLabel+"-previous");previousSpan.appendChild(document.createTextNode(this.options.paginationLeft));pagination.appendChild(previousSpan);var halfTotalNavPages=Math.floor(options.maxPaginationLinks/2);for(var i=1;i<=numPages;i++)
{var span=document.createElement("span");span.setAttribute("id",options.baseName+"-"+cssLabel+"-page"+i);if(i==1)
{span.setAttribute("class",options.baseName+"-"+cssLabel+"-selected");span.setAttribute("className",options.baseName+"-"+cssLabel+"-selected");}
if(i>halfTotalNavPages)
span.style.cssText="display:none";var a=document.createElement("a");a.setAttribute("href","#");a.onclick=this.changePage.bindAsEventListener(this,i);a.appendChild(document.createTextNode(i));span.appendChild(a);pagination.appendChild(span);}
var nextSpan=document.createElement("span");nextSpan.setAttribute("id",options.baseName+"-"+cssLabel+"-next");nextSpan.appendChild(this._getPaginationNextLinkNode());pagination.appendChild(nextSpan);$(options.baseName+"-"+cssLabel).appendChild(pagination);},_updatePaginationGroup:function(cssLabel,selectedFlagItems,page)
{var options=this.options;var currentPage=this.currentPage;$(options.baseName+"-"+cssLabel+"-page"+currentPage).removeClassName(options.baseName+"-"+cssLabel+"-selected");$(options.baseName+"-"+cssLabel+"-page"+page).addClassName(options.baseName+"-"+cssLabel+"-selected");var lastPage=Math.ceil(selectedFlagItems.length/options.numItemsPerPage);if(page==1)
$(options.baseName+"-"+cssLabel+"-previous").innerHTML=options.paginationLeft;else
{$(options.baseName+"-"+cssLabel+"-previous").innerHTML="";$(options.baseName+"-"+cssLabel+"-previous").appendChild(this._getPaginationPreviousLinkNode());}
if(page==lastPage)
$(options.baseName+"-"+cssLabel+"-next").innerHTML=options.paginationRight;else
{$(options.baseName+"-"+cssLabel+"-next").innerHTML="";$(options.baseName+"-"+cssLabel+"-next").appendChild(this._getPaginationNextLinkNode());}
var totalVisible=0;var halfTotalNavPages=Math.floor(options.maxPaginationLinks/2);var firstVisiblePage=(page>halfTotalNavPages)?page-halfTotalNavPages:1;var lastVisiblePage=((page+halfTotalNavPages)<lastPage)?page+halfTotalNavPages:lastPage;for(var i=1;i<=lastPage;i++)
{if(i<firstVisiblePage)
$(options.baseName+"-"+cssLabel+"-page"+i).hide();if(i>lastVisiblePage)
$(options.baseName+"-"+cssLabel+"-page"+i).hide();if(i>=firstVisiblePage&&i<=lastVisiblePage)
$(options.baseName+"-"+cssLabel+"-page"+i).show();}},_getFlagCountFromFlagIndex:function(flagIndex)
{var flagCount=null;this.flagInfo.each(function(pair){var key=pair.key;var value=pair.value;if(flagIndex==value[0])
flagCount=value[1];});return flagCount;},_getItemsByFlag:function()
{var flagIndex=this.currentFlag;var flagIndex2=this.currentFlag2;var nodes=[];for(var i=0;i<this.listItems.length;i++)
{var inFirstDropdown=false;if(this.itemFlagIndexes[i].include(flagIndex)||flagIndex=="dd1-all")
inFirstDropdown=true;var inSecondDropdown=true;if(this.hasSecondDropdown)
{if(!this.itemFlagIndexes[i].include(flagIndex2)&&flagIndex2!="dd2-all")
inSecondDropdown=false;}
if(inFirstDropdown&&inSecondDropdown)
nodes.push(this.listItems[i]);}
return nodes;},_getNumItemsByFlag:function()
{return this._getItemsByFlag().length;},_getPaginationNextLinkNode:function()
{var nextLink=document.createElement("a");nextLink.setAttribute("href","#");nextLink.onclick=this.changePage.bindAsEventListener(this,"next");nextLink.appendChild(document.createTextNode(this.options.paginationRight));return nextLink;},_getPaginationPreviousLinkNode:function()
{var previousLink=document.createElement("a");previousLink.setAttribute("href","#");previousLink.onclick=this.changePage.bindAsEventListener(this,"previous");var left=this.options.paginationLeft;previousLink.appendChild(document.createTextNode(left));return previousLink;},_selectDropdownOption:function(flagIndex,ddNum)
{var cssLabel=(ddNum==1)?"dropdown":"dropdown2";var options=this.options;var dd_div=$(options.baseName+"-flag-"+cssLabel).getElementsByTagName("select");var dd=dd_div[0];for(var i=0;i<dd.options.length;i++)
{if(dd.options[i].value==flagIndex)
{dd.options[i].selected=true;break;}}},_getFlagDropdownNum:function(flagIndex)
{var ddNum=1;if(this.hasSecondDropdown)
{if(flagIndex=="dd2-all")
ddNum=2;this.flagInfo.each(function(pair){var index=pair.value[0];if(index==flagIndex)
ddNum=pair.value[2];});}
return ddNum;},_shouldDisplayItem:function(flagIndexes)
{var shouldDisplay=false;if(flagIndexes.include(this.currentFlag)||this.currentFlag=="dd1-all")
{shouldDisplay=true;if(this.hasSecondDropdown)
{shouldDisplay=false;if(flagIndexes.include(this.currentFlag2)||this.currentFlag2=="dd2-all")
shouldDisplay=true;}}
return shouldDisplay;}};