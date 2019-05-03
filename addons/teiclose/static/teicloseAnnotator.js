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

function fileChange (file){
    window.project = window.location.pathname.split('/')[1]
    window.file = window.location.pathname.split('/')[3]
    window.version = window.location.pathname.split('/')[4]

    const sidepanel = new SidePanel();
    const model = new Model(sidepanel);
    const panel = new Panel(model);
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
      document.getElementById('editor').onselectionchange = ()=>panel.handleSelection();

    document.getElementById('toggle-timeline-details').addEventListener('click', ()=>timeline.toggleDetails())

    for(let input of document.getElementById('display-options').getElementsByTagName('input'))
        input.addEventListener('click', handleDisplayChange);

    model.loadTEI(model.fromText, file);
}

function handleDisplayChange(evt){ 
    $('div#annotator-root').attr(evt.target.id,evt.target.checked);
}


function getUserSelection(model) {
    let text = "", selection;
    let node = null;
    if (window.getSelection) {
        selection = window.getSelection();
        text = selection.toString();
    }else if (document.selection && document.selection.type != "Control"){
        selection = document.selection;
        text = document.selection.createRange().text;
    }

    const selection_range = selection.getRangeAt(0),
        start_range = document.createRange(),
        end_range = document.createRange();

    start_range.setStart($('#editor page')[0], 0);
    start_range.setEnd(selection_range.startContainer,selection_range.startOffset);

    end_range.setStart($('#editor page')[0], 0);
    end_range.setEnd(selection_range.endContainer,selection_range.endOffset);

    const start_fragment = start_range.cloneRange().cloneContents(),
        end_fragment = end_range.cloneRange().cloneContents();

    const start_container = document.createElement('div'),
        end_container = document.createElement('div');

    start_container.appendChild(start_fragment);
    end_container.appendChild(end_fragment);

    const start_content = start_container.innerHTML,
        end_content = end_container.innerHTML;
    
    let body_start_offset = 0;
    for(let i=0; i<start_content.length; i++){
        if(start_content[i]!=end_content[i]){
            body_start_offset = i+1;
            break;
        }
    }

    let body_end_offset = 0;
    for(let i=0; i<end_content.length; i++){
        if(model.TEIbody[i]!=end_content[i]){
            body_end_offset = i;
            break;
        }
    }

    const abs_positions = [
        model.TEIheaderOffset+body_start_offset,
        model.TEIheaderOffset+body_end_offset
    ]

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

function Model(sidepanel){
    this.sidePanel = sidepanel;
    this.TEIheader=null;
}

Model.prototype.createAnnotation = function(range, annotation_){
    const annotation = annotation_.renderHTML();
    annotation.addEventListener('mouseenter', (evt)=>this.sidePanel.show(evt));
    annotation.addEventListener('mouseleave', (evt)=>this.sidePanel.hide(evt));
    let contents = range.extractContents();
    annotation.appendChild(contents);
    range.insertNode(annotation);
    this.updateStatistics()
    $('div#annotator-root').toggleClass('topPanelDisplayed');
}

Model.prototype.exportTEI = function(){
    let doc = this.TEIheader+document.getElementById('editor').innerHTML+'</TEI>';
    doc = doc.replace(/<page.*>/gm,"");
    doc = doc.replace(/<\/page>/gm,"");

    //Download the TEI
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(doc));
    element.setAttribute('download', 'tei.xml');

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
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

Model.prototype.loadTEI = function(method, file){
    const self_ = this;

    method(file).then((xml=>{
        const reader = new TEIreader(xml.content);
        //console.log(reader)
        $("#toolbar-header span#name").html(xml.name)
        this.TEIbody = reader.body();
   
        $('#editor page').html(this.TEIbody);
   
        this.updateStatistics();

        for(annotation of Array.from(document.getElementsByTagName('certainty'))){
            annotation.addEventListener('mouseenter', (e)=>this.sidePanel.show(e));
            annotation.addEventListener('mouseleave', (e)=>this.sidePanel.hide(e));
        }
        this.TEIheader = reader.header();
        this.TEIheaderOffset = reader.headerOffset();
        this.TEItext = reader.doc;
        const parser = new DOMParser();
        this.TEIdoc = parser.parseFromString(reader.doc, 'text/xml');
    }));
}

Model.prototype.updateStatistics = function(){
    const authors = Array.from($('certainty')).reduce((acd,c)=>acd.add(c.attributes['author'].value),new Set()).size;
    $("div#stats").html(`Total annotations : <span>${$('certainty').length} </span> Total contributors : <span>${authors} </span>
            Place : <span>Ireland </span>Date of creation : <span>None </span>`)

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

function Panel(model_){
    this.annotation = new Annotation();
    this.shown = false;
    this.range = document.createRange();
    this.text = '';
    this.model = model_
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

Panel.prototype.handleSelection = function(evt){
    const selection = getUserSelection(this.model);
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
            "start_pos": this.selection.abs_positions[0],
            "end_pos": this.selection.abs_positions[1],
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
    
    this.model.createAnnotation(this.range,annotation);
}

Panel.prototype.updateAnnotation = function(){}

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

/* TEIreader
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 * */

function TEIreader(doc) {
    this.doc = doc.replace(/\r/gm," ");;
    this.header_ = "";
    this.body_= "";
    this.parsed = false;
}

TEIreader.prototype.headerOffset = function(){
    if(this.parsed === false)
        this._parse();
    return this.headerOffset_;
}

TEIreader.prototype.header = function(){
    if(this.parsed === false)
        this._parse();
    return this.header_;
}

TEIreader.prototype.body = function(){
    if(this.parsed === false)
        this._parse();
    return this.body_;
}

// Parse the doc to extract both the header and bod
TEIreader.prototype._parse = function(){
    let reading_tag = false, tag="", header=true;

    this.body_ = '';

    for(let i =0; i<this.doc.length; i++){
        if(this.doc[i] == '<'){
            reading_tag = true;
            tag="";
        }else if(reading_tag === true && this.doc[i] == '>'){
            if(tag.includes('/teiHeader')){
                header = false;
                this.header_ += '>';
                reading_tag = false;
                // Just count \r caracters
                //this.headerOffset_ = this.header_.replace(/\r/gm,"").length+1
                // Count \r too
                this.headerOffset_ = i+1
                continue;
            }
            reading_tag = false;
        }

        if(reading_tag===true)
            tag+=this.doc[i];
        
        if(header===true)
            this.header_+=this.doc[i];
        else
            this.body_+=this.doc[i];
   
    }

    this.parsed =true;
    return this;
}

module.exports = {
    fileChange
};
