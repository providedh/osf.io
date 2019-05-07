require('./teicloseAnnotator.css');
window.API_urls = require('./annotationApiUrlBuilder.js').API_urls;

const versions = [
    {"url": "","timestamp": "2018-4-1","imprecision": 0,"ignorance": 1,"credibility": 2,"incompleteness": 0 },
    {"url": "","timestamp": "2018-6-12","imprecision": 0,"ignorance": 3,"credibility": 2,"incompleteness": 0},
    {"url": "","timestamp": "2018-8-14","imprecision": 3,"ignorance": 5,"credibility": 2,"incompleteness": 0},
    {"url": "","timestamp": "2018-8-22","imprecision": 3,"ignorance": 5,"credibility": 9,"incompleteness": 2},
    {"url": "","timestamp": "2019-1-19","imprecision": 3,"ignorance": 6,"credibility": 14,"incompleteness": 5}
];

function saveVersion(){
    $.ajax({
        url: API_urls.get_save_url(window.project, window.file),
        type: 'PUT',   //type is any HTTP method
        data: {},      //Data as js object
        success: function (a) {
            console.log('save - success < ',API_urls.get_save_url(window.project, window.file),' < ',a)
        },
        error: function (a) {
            console.log('save - error < ',API_urls.get_save_url(window.project, window.file),' < ',a)
        }
    })
}


function updateStatistics(){
    const authors = Array.from($('certainty')).reduce((acd,c)=>acd.add(c.attributes['author'].value),new Set()).size;
    $("div#stats").html(`Total annotations : <span>${$('certainty').length} </span> Total contributors : <span>${authors} </span>
            Place : <span>Ireland </span>Date of creation : <span>None </span>`)

}

function fileChange (file){
    window.project = window.location.pathname.split('/')[1]
    window.file = window.location.pathname.split('/')[3]
    window.version = window.location.pathname.split('/')[4]

    const sidepanel = new SidePanel();
    const model = new Model();
    const panel = new Panel();
    const timeline = new Timeline();
    timeline.renderTimestamps();

    // Add event handlers for all the application
    document.getElementById("attribute-name-input").setAttribute('locus', 
        document.getElementById('locus').value);
    document.getElementById('locus').addEventListener('change', (evt)=>{
        if(evt.target.value == 'value')
            document.getElementById('value').value = document.getElementById('references').value;
        document.getElementById("attribute-name-input").setAttribute('locus', evt.target.value);
    }, false);

    document.getElementById('saveFile').addEventListener('click', ()=>saveVersion());
    document.getElementById('openPanel').addEventListener('click', ()=>panel.show());
    document.getElementById('closePanel').addEventListener('click', ()=>panel.hide());

    document.getElementById('create-annotation').addEventListener('click', ()=>panel.createAnnotation());

    document.getElementById('editor').onmouseup = 
      document.getElementById('editor').onselectionchange = ()=>panel.handleSelection(model);

    document.getElementById('toggle-timeline-details').addEventListener('click', ()=>timeline.toggleDetails())

    for(let input of document.getElementById('display-options').getElementsByTagName('input'))
        input.addEventListener('click', handleDisplayChange);

    model.loadTEI(model.fromText, file).then(()=>{
        for(annotation of Array.from(document.getElementsByTagName('certainty'))){
            annotation.addEventListener('mouseenter', (e)=>sidepanel.show(e));
            annotation.addEventListener('mouseleave', (e)=>sidepanel.hide(e));
        }
    });
}

function handleDisplayChange(evt){ 
    $('div#annotator-root').attr(evt.target.id,evt.target.checked);
}

function contentsFromRange(startNode, startOffset, endNode, endOffset){
    const selection = document.createRange();

    selection.setStart(startNode, startOffset);
    selection.setEnd(endNode,endOffset);

    const fragment = selection.cloneRange().cloneContents(),
        container = document.createElement('div');

    container.appendChild(fragment);

    return container.innerHTML;
}

function getUserSelection(model) {

    let text = "", selection, node = null;
    if (window.getSelection) {
        selection = window.getSelection();
        text = selection.toString();
    }else if (document.selection && document.selection.type != "Control"){
        selection = document.selection;
        text = document.selection.createRange().text;
    }

    const selection_range = selection.getRangeAt(0);

    let start_content = contentsFromRange($('#editor page')[0], 0, selection_range.startContainer,selection_range.startOffset),
        end_content = contentsFromRange($('#editor page')[0], 0, selection_range.endContainer,selection_range.endOffset);

    for(empty_tag of model.TEIemptyTags){
        console.log(model.expandedEmptyTag(empty_tag), empty_tag);
        start_content = start_content.replace(model.expandedEmptyTag(empty_tag), empty_tag);
        end_content = end_content.replace(model.expandedEmptyTag(empty_tag), empty_tag);
    }

    console.log('replaced')
    console.log(model.TEIbody)
    console.log(end_content)
    console.log(model.TEIheaderLength)

    const abs_positions = {
        start: 0,
        end: 0
    };

    for(let i=0; i<start_content.length; i++){
        if(model.TEIbody[i]!=start_content[i]){
            abs_positions.end = model.TEIheaderLength + i + 1;
            break;
        }
    }

    for(let i=0; i<end_content.length; i++){
        if(model.TEIbody[i]!=end_content[i]){
            abs_positions.start = model.TEIheaderLength + i;
            break;
        }
    }

    return {text:text, range:selection_range, abs_positions:abs_positions};
}

/* Timeline
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 * */
function timeScale(domain_, range_){
    const domain = [
        domain_.reduce((a,b)=>a<b?a:b),
        domain_.reduce((a,b)=>a>b?a:b)
    ], range = [
        Math.min(...range_),
        Math.max(...range_)
    ];

    return (t)=>{
        //   24 hrs/day * 60 minutes/hour * 60 seconds/minute * 1000 msecs/second
        const msDomainRange = domain[1]-domain[0];
        const daysDomainRange = Math.floor(msDomainRange/(1000 * 60 * 60  * 24));

        const msTrange = t - domain[0];
        const daysTrange = Math.floor(msTrange/(1000 * 60 * 60  * 24));

        return range[0] + (range[1]*(daysTrange/daysDomainRange));
    }
}

function linearScale(domain_, range_){
    const domain = [
        Math.min(...domain_),
        Math.max(...domain_)
    ], range = [
        Math.min(...range_),
        Math.max(...range_)
    ], domRange = domain[1] - domain[0];

    return (x)=>{
        return range[0] + (range[1]*((x-domain[0])/domRange));
    }
}

function Timeline(){
    this.width = "21cm";
    this.displayDetails = false;
    this.detailsRendered = false;
}

Timeline.prototype.renderTimestamps = function(){
    const timestamps = versions.map(x=>new Date(...x.timestamp.split('-'))),
        firstDate = timestamps.reduce((a,b)=>a<b?a:b),
        lastDate = timestamps.reduce((a,b)=>a>b?a:b),
        xScale = timeScale([firstDate, lastDate],[0,20.8]);

    let element = null, offset = 0;
    for(let timestamp of versions){
        offset = xScale(new Date(...timestamp.timestamp.split('-')));

        element = document.createElement('div');
        element.setAttribute('class','timestamp');
        element.style = `left:${offset}cm`;

        element.addEventListener('mouseenter', (evt)=>this.handleTimestampMouseenter(evt,timestamp));
        element.addEventListener('mouseleave', (evt)=>this.handleTimestampMouseleave(evt,timestamp));

        document.getElementById('time-bar').appendChild(element);
    }
}

Timeline.prototype.renderDetails = function(){
    $('div#time-bar canvas').attr('width', $('div#timeline hr').width());
    $('div#time-bar canvas').attr('height', $('div#timeline hr').height());

    const timestamps = versions.map(x=>new Date(...x.timestamp.split('-'))),
        firstDate = timestamps.reduce((a,b)=>a<b?a:b),
        lastDate = timestamps.reduce((a,b)=>a>b?a:b),
        width = Math.trunc($('div#time-bar canvas').width()+1),
        height = Math.trunc($('div#time-bar canvas').height()-2),
        max = Math.max(...Array.prototype.concat(...versions.map(x=>([
                x.imprecision,
                x.credibility,
                x.ignorance,
                x.incompleteness
            ])))),
        yScale = linearScale([0,max],[0,height]),
        xScale = timeScale([firstDate, lastDate],[0,width]),
        canvasCtx = $('div#time-bar canvas')[0].getContext('2d');

    const renderVersions = (uncertainty, color)=>{
        canvasCtx.beginPath();
        canvasCtx.moveTo(0,height);

        for(let d of versions){
            canvasCtx.lineTo(xScale(new Date(...d.timestamp.split('-'))),height-yScale(d[uncertainty]));
        }

        const last = versions[versions.length-1];
        canvasCtx.lineTo(xScale(new Date(...last.timestamp.split('-'))),height);
        canvasCtx.lineTo(0,height);

        canvasCtx.fillStyle = `rgba(${color[0]},${color[1]},${color[2]},0.07)`;
        canvasCtx.strokeStyle = `rgb(${color[0]},${color[1]},${color[2]})`;

        canvasCtx.fill();
        canvasCtx.stroke();
    }

    renderVersions('imprecision',[148,15,137]);
    renderVersions('credibility',[218,136,21]);
    renderVersions('ignorance',[23,85,141]);
    renderVersions('incompleteness',[174,210,21]);
}

Timeline.prototype.showDetails = function(){
    document.getElementById('toggle-timeline-details').innerText = "( Hide details )";
    $('div#annotator-root').toggleClass('timelineExpanded');
    if(this.detailsRendered === false){
        this.renderDetails();
        this.detailsRendered = true;
    }
}

Timeline.prototype.hideDetails = function(){
    document.getElementById('toggle-timeline-details').innerText = "( Show details )";
    $('div#annotator-root').toggleClass('timelineExpanded')
}

Timeline.prototype.toggleDetails = function(){
    this.displayDetails = !this.displayDetails;
    if(this.displayDetails === true)
        this.showDetails();
    else
        this.hideDetails();
}

Timeline.prototype.handleTimestampMouseenter = function(evt,timestamp){
    const popup = document.getElementById('popup');
    const max = Math.max(timestamp.imprecision,timestamp.incompleteness,
        timestamp.ignorance,timestamp.credibility),
        xScale = linearScale([0,max],[0,6]);

    popup.innerHTML=`Timestamp : ${timestamp.timestamp}<br>
      Author : _@email.com<br>
      <div class="content">
      <span>
        Imprecision uncertainty</br>
        Incompleteness uncertainty</br>
        Credibility uncertainty</br>
        Ignorance uncertainty
      </span>
      <span>
        <span class="color uncertainty" author="me" title="high"
            style="width:${xScale(timestamp.imprecision)}em;" source="imprecision" cert="high"></span></br>
        <span class="color uncertainty" author="me" title="high" 
            style="width:${xScale(timestamp.incompleteness)}em;" source="incompleteness" cert="high"></span></br>
        <span class="color uncertainty" author="me" title="high" 
            style="width:${xScale(timestamp.ignorance)}em;" source="ignorance" cert="high"></span></br>
        <span class="color uncertainty" author="me" title="high" 
            style="width:${xScale(timestamp.credibility)}em;" source="credibility" cert="high"></span></br>
      </span>
      <span>
        ${timestamp.imprecision}</br> 
        ${timestamp.incompleteness}</br> 
        ${timestamp.ignorance}</br> 
        ${timestamp.credibility}
      </span>
      </div>
    `;
    popup.style.left = evt.target.style.left;
    popup.style.display="block";
}

Timeline.prototype.handleTimestampMouseleave = function(evt){
    document.getElementById('popup').style.display="none";
}

/* Model
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 * */

function Model(){
    this.TEIheader=null;
}

Model.prototype.fromTag = function(f){
    return new Promise((resolve)=>{
        resolve({content:document.getElementsByTagName('teifile')[0].textContent, 
            name:document.getElementsByTagName('teifile')[0].attributes['filename'].value});
    });
}

Model.prototype.fromLocalFile = function(f){
    return new Promise((resolve)=>{
        let r = new FileReader();
        r.onload = function(e) {
            let contents = e.target.result;
            resolve({content:contents, name:f.name});
        };

        r.readAsText(f);
    });
}

Model.prototype.fromText = function(text){
    return new Promise((resolve)=>{
        resolve({'content': text});
    });
}

Model.prototype.expandedEmptyTag = function(empty_tag){
    const tag_name = empty_tag.slice(1).split(' ')[0],
        opening_tag = empty_tag.replace('/>','>'),
        closing_tag = '</'+tag_name+'>';

    return opening_tag + closing_tag;
}

Model.prototype.loadTEI = function(method, file){
    const self_ = this;

    return new Promise((resolve, error)=>{
        method(file).then((xml=>{
            const sanityzed_xml = xml.content.replace(/\r/gm," "),
                body_replaced_xml = sanityzed_xml.replace(/body>/gm, 'page>'), // Creating a separate div would alter structure
                parsed_tei = $.parseXML(body_replaced_xml).documentElement,
                body = parsed_tei.getElementsByTagName('page')[0];
            
            this.TEItext = parsed_tei.outerHTML.replace(' xmlns="http://www.tei-c.org/ns/1.0"', '');
            this.TEIbody = body.innerHTML.replace(' xmlns="http://www.tei-c.org/ns/1.0"', '');
            this.TEIemptyTags = body.innerHTML.match(/<[^>]+\/>/gm);
            this.TEIheaderLength = parsed_tei.outerHTML.indexOf('<page>');

            body.setAttribute('size', 'A4');
            $('#editor').append(body);

            
            console.log(body, this.TEIemptyTags)
           
            updateStatistics();
        }));
        resolve();
    });
}

/* Side panel
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 * */
function SidePanel(){
    this.shown = false;
    this.attributes = ['locus','cert','author','value','proposedvalue','source'];
}
SidePanel.prototype.show = function(evt){
    for(let attr of this.attributes){
        $('div#side-panel span#'+attr).text(' '+evt.target.attributes[attr].value);
    }

    $('div#side-panel div#text').text(evt.target.innerText);
    let id = evt.target.childNodes[0].nodeName.toLowerCase();
    id = id!='#text'?id:evt.target.parentNode.nodeName.toLowerCase();
    $('div#side-panel span.teiLegendElement').attr('id',id);
    $('div#side-panel span#parent').text(id);

    const text = document.getElementById('editor').innerText,
        exp = new RegExp(evt.target.innerText,'g'),
        result = text.match(exp);
    $('div#side-panel div#tag-stats #times').text(' '+(result?result.length-1:0));

    const tags = Array.from(document.getElementsByTagName('certainty')).reduce((acd,c)=>acd+(c.innerText.includes(evt.target.innerText)?1:0),0)
    $('div#side-panel div#tag-stats #tags').text(' '+(tags-1));
    $('div#side-panel div#certrange').attr('class',evt.target.attributes['cert'].value)
    $('div#annotator-root').toggleClass('sidePanelDisplayed');

    const desc = Array.from(evt.target.childNodes).filter(x=>x.nodeName.toLowerCase()=="desc");
    if(desc && desc.length >= 1)
        $('div#side-panel div#desc').html(
            `<b>Description :</b><br/><span>${desc[0].innerText}</span>`);
    else
        $('div#side-panel div#desc').html('');

    if(evt.target.attributes['locus'].value == 'value'){
        $('div#side-panel span#lev-dist')
            .html(`<b>Levenshtein distance with propposed value : </b>${this.levenshtein(
                evt.target.attributes['value'].value,      
                evt.target.attributes['proposedvalue'].value
        )}`);
    }else
        $('div#side-panel span#lev-dist').html('');


    this.shown = true;
}

SidePanel.prototype.hide = function(){
    $('div#annotator-root').toggleClass('sidePanelDisplayed');
    this.shown = false;
}

SidePanel.prototype.levenshtein = function(a,b){
    if(a.length == 0) return b.length;
    if(b.length == 0) return a.length;
  
    row = Array.from(Array(a.length + 1)).map((x,i,c)=>i)
  
    for (i = 1,prev=1; i <= b.length; i++,prev++) {
        for (j = 1; j <= a.length; j++) {
            val = (b[i-1] === a[j-1])?row[j-1]:Math.min(
            row[j-1] + 1,       // substitution
            Math.min(prev + 1,  // insertion
            row[j] + 1));       // deletion
      
            row[j - 1] = prev
            prev = val
        }
        row[a.length] = prev
    }
    return row[a.length] 
}
/* Panel
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 * */

function Panel(){
    this.annotation = new Annotation();
    this.shown = false;
    this.range = document.createRange();
    this.text = '';
}

Panel.prototype.changeAnnotation = function(annotation_){
    this.annotation = annotation_;
}

Panel.prototype.show = function(){
    $('div#annotator-root').addClass('topPanelDisplayed');
    this.shown = true;
}

Panel.prototype.hide = function(){
    $('div#annotator-root').removeClass('topPanelDisplayed');
    this.shown = false;
    this.range = document.createRange();
    Array.from($("#top-panel input"), x=>x).map(i=>i.value = '');
}

Panel.prototype.handleSelection = function(model){
    const selection = getUserSelection(model);
    console.log(selection);
    if(selection.range.collapsed === false){

        $('section#top-panel #references').val(selection.text);   

        this.range = selection.range;
        this.selection = selection;
        this.show();
    }
}

Panel.prototype.createAnnotation = function(){
    const values = {};
    Array.from($("#top-panel input"), x=>x).map(i=>values[i.id]=i.value);
    Array.from($("#top-panel select"), x=>x).map(i=>values[i.id]=i.value);
    if(values['locus'] == 'value')
        values['value'] = values['references'];

    const annotation = (new Annotation()).fromDict(values);
    
    const url = API_urls.get_add_annotation_url(window.project, window.file);
    const data = {
            "start_pos": this.selection.abs_positions.start,
            "end_pos": this.selection.abs_positions.end,
            "source": values.source,
            "locus": values.locus,
            "certainty": values.cert,
            "asserted_value": values.proposedValue,
            "description": values.desc,
            "tag": "xxx"
        }

    if(values['locus'] == 'attribute')
        data['attribute'] = values['attributeName'];
    
    $.ajax({
        url: url,
        type: 'PUT',   //type is any HTTP method
        contentType: "application/json; charset=UTF-8",
        data: JSON.stringify(data),      //Data as js object
        scriptCharset: 'utf8',
        success: function (a) {
            console.log('annotate - success < ',a)
        },
        error: function(data) {
            console.log('annotate - error < ', data);
        }
    })
}

/* Annotation
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 * */

function Annotation(){
    this.locus = '';
    this.cert = '';
    this.value = '';
    this.proposedValue = '';
    this.source = '';
    this.desc = ''
}

Annotation.prototype.fromDict = function(values){
    const {locus, cert, value, proposedValue, source, desc} = values;

    this.locus = locus;
    this.cert = cert;
    this.value = value;
    this.proposedValue = proposedValue;
    this.source = source;
    this.desc = desc;

    return this;
}

Annotation.prototype.fromHTMLelement = function(){
    return this;
}

Annotation.prototype.fromTEIelement = function(){
    return this;
}

Annotation.prototype.update = function(_val){

}

// Returns the html for such Annotation
Annotation.prototype.renderHTML = function(){
    let attr;
    let annotation = document.createElement('certainty');
    let desc;

    annotation.setAttribute('locus', this.locus);
    annotation.setAttribute('cert', this.cert);
    annotation.setAttribute('author', 'me');
    annotation.setAttribute('value', this.value);
    annotation.setAttribute('proposedValue', this.proposedValue);
    annotation.setAttribute('source', this.source);
    annotation.setAttribute('title',
        `${this.source} cert=${this.cert} locus=${this.locus}`);

    if(this.desc != ''){
        desc = document.createElement('desc');
        desc.innerText = this.desc;
        annotation.appendChild(desc);
    }


    return annotation;
}

// Returns the TEI XML code for such annotation
Annotation.prototype.renderTEI = function(){}

module.exports = { fileChange };