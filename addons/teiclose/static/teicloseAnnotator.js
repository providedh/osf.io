require('./teicloseAnnotator.css');
var d3 = require('d3');
window.API_urls = require('./annotationApiUrlBuilder.js').API_urls;
window.colorSchemes = require('./teicloseColorSchemes.js').colorSchemes;

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
    $("div#stats #annotations").html($('certainty').length);
    $("div#stats #authors").html(authors);
}

function updateTimeStatistics(date){
    $("div#stats #date").html(date.toDateString());
}

function getAnnotatorAttribute(attr){
    return document.getElementById('annotator-root').attributes[attr].value;
}

function setAnnotatorAttribute(attr, val){
    return document.getElementById('annotator-root').setAttribute(attr, val);
}

function setup(file){
    window.project = window.location.pathname.split('/')[1]
    window.file = window.location.pathname.split('/')[3]
    window.version = window.location.pathname.split('/')[4]

    const sidepanel = new SidePanel();
    const model = new Model();
    const panel = new Panel();
    const timeline = new Timeline();

    $.ajax({
        url: API_urls.get_history_url(window.project, window.file, window.version),
        type: 'GET',   //type is any HTTP method
        data: {},      //Data as js object
        success: function (history) {
            const currentDate = new Date(history[history.length-1].timestamp);
            updateTimeStatistics(currentDate);
            timeline.loadHistory(history);
            timeline.renderTimestamps();
            document.getElementById('toggle-timeline-details').addEventListener('click', ()=>timeline.toggleDetails());
        },
        error: function (a) {
            console.log('save - error < ',API_urls.get_save_url(window.project, window.file),' < ',a)
        }
    })

    // Setup the annotation controls based on the locus
    const annotationType = $("#annotation-options input:checked")[0].value,
        locus = document.getElementById('locus').value;

    setAnnotatorAttribute('locus', locus);
    setAnnotatorAttribute('annotation', annotationType);

    panel.updateControls(annotationType, locus);

    // Setup visual attributes based on selections
    Object
        .values($('#display-options input[type=checkbox]'))
        .forEach(input=>$('div#annotator-root').attr(input.id, input.checked));

    // Add event handlers for all the application
    document.getElementById("attribute-name-input").setAttribute('locus', 
        document.getElementById('locus').value);
    document.getElementById('locus').addEventListener('change', (evt)=>{
        setAnnotatorAttribute('locus', evt.target.value);
        panel.updateControls(getAnnotatorAttribute('annotation'), evt.target.value);
    }, false);

    for(let input of document.getElementById('annotation-options').getElementsByTagName('input'))
        input.addEventListener('click', (e)=>{
        setAnnotatorAttribute('annotation', e.target.value);
        panel.updateControls(e.target.value, getAnnotatorAttribute('locus'));
    });

    // Add event handlers for all the application
    document.getElementById('saveFile').addEventListener('click', ()=>saveVersion());
    document.getElementById('openPanel').addEventListener('click', ()=>panel.show());
    document.getElementById('closePanel').addEventListener('click', ()=>panel.hide());

    document.getElementById('create-annotation').addEventListener('click', ()=>panel.createAnnotation());

    document.getElementById('editor').onmouseup = 
      document.getElementById('editor').onselectionchange = ()=>panel.handleSelection(model);

    for(let input of document.getElementById('display-options').getElementsByTagName('input'))
        input.addEventListener('click', handleDisplayChange);

    fileChange(model, sidepanel, file);
    window.updateFile = (f)=>fileChange(model, sidepanel, f); 
}

function fileChange (model, sidepanel, file){
    model.loadTEI(file).then((tei_doc)=>{
        console.log({d3:d3})
        for(annotation of Array.from(document.getElementsByTagName('certainty'))){
            annotation.addEventListener('mouseenter', (e)=>sidepanel.show(e.target,e.target.textContent, annotation.parentNode.nodeName));
            annotation.addEventListener('mouseleave', (e)=>sidepanel.hide());
        }

        const page = document.getElementsByTagName('page')[0];
        let identifyed = Array.from(page.getElementsByTagName('*'), a=>a.attributes['xml:id']?a:null);
        identifyed = identifyed.filter(x=>x!=null);
        const identifyed_map = Object.fromEntries(identifyed.map(x=>[x.attributes['xml:id'].value, x]));

        Array.from(tei_doc.getElementsByTagName('teiHeader')[0].getElementsByTagName('certainty'), a=>a)
            .forEach(annotation=>{
                annotation.attributes['target'].value.split(" ").forEach(target=>{
                    const node = document.getElementById(target.slice(1));
                    if(node != null){
                        node.addEventListener('mouseenter', ()=>sidepanel.show(annotation,node.textContent, node.nodeName));
                        node.addEventListener('mouseleave', ()=>sidepanel.hide());       
                        addStyles(
                            target.slice(1), 
                            annotation.attributes['source'].value, 
                            annotation.attributes['cert'].value
                            );
                    }
                })
            });
        updateStatistics();
    });
}

function addStyles(id, source, cert){
    const greyRule = 'div#annotator-root[display-uncertainty=true] ' 
        + '#'+id
        + '{background-color: lightgrey;}';
    const colorRule = 'div#annotator-root[display-uncertainty=true][color-uncertainty=true] ' 
        + '#'+id
        + `{background-color: ${window.colorSchemes[source][cert]};}`;

    document.styleSheets[0].insertRule(greyRule);
    document.styleSheets[0].insertRule(colorRule);
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
        start_content = start_content.replace(model.expandedEmptyTag(empty_tag), empty_tag);
        end_content = end_content.replace(model.expandedEmptyTag(empty_tag), empty_tag);
    }

    const positions = [];

    for(let i=0; i<start_content.length; i++){
        if(model.TEIbody[i]!=start_content[i]){
            positions.push(model.TEIheaderLength + i);
            break;
        }
    }

    for(let i=0; i<end_content.length; i++){
        if(model.TEIbody[i]!=end_content[i]){
            positions.push(model.TEIheaderLength + i);
            break;
        }
    }

    const abs_positions = {start: Math.min(...positions), end: Math.max(...positions)};

    return {text:text, range:selection_range, abs_positions:abs_positions};
}

/* Timeline
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 * */
function Timeline(){
    this.width = "21cm";
    this.displayDetails = false;
    this.detailsRendered = false;
    this.history = [];
}

Timeline.prototype.loadHistory = function(history){
    this.history = history;
}

Timeline.prototype.renderTimestamps = function(){
    const timestamps = this.history.map(x=>new Date(x.timestamp)),
        xScale = d3.scaleTime()
            .domain([Math.min(...timestamps),Math.max(...timestamps)])
            .range([0,20.8]);

    let element = null, offset = 0;
    for(let timestamp of this.history){
        offset = xScale(new Date(timestamp.timestamp));

        element = document.createElement('a');
        element.setAttribute('class','timestamp');
        element.setAttribute('href',timestamp.url);
        element.style = `left:${offset}cm`;

        element.addEventListener('mouseenter', (evt)=>this.handleTimestampMouseenter(evt,timestamp));
        element.addEventListener('mouseleave', (evt)=>this.handleTimestampMouseleave(evt,timestamp));



        document.getElementById('time-bar').appendChild(element);
    }
}

Timeline.prototype.renderDetails = function(){
    $('div#time-bar canvas').attr('width', $('div#timeline hr').width());
    $('div#time-bar canvas').attr('height', $('div#timeline hr').height());

    const timestamps = this.history.map(x=>new Date(...x.timestamp.split('-'))),
        width = Math.trunc($('div#time-bar canvas').width()+1),
        height = Math.trunc($('div#time-bar canvas').height()-2),
        max = Math.max(...Array.prototype.concat(...this.history.map(x=>([
                x.imprecision,
                x.credibility,
                x.ignorance,
                x.incompleteness
            ])))),
        yScale = d3.scaleLinear().domain([0,max]).range([0,height]),
        xScale = d3.scaleTime()
            .domain([Math.min(...timestamps),Math.max(...timestamps)])
            .range([0,width]),
        canvasCtx = $('div#time-bar canvas')[0].getContext('2d');

    const renderVersions = (uncertainty, color)=>{
        canvasCtx.beginPath();
        canvasCtx.moveTo(0,height);

        for(let d of this.history){
            canvasCtx.lineTo(xScale(new Date(d.timestamp)),height-yScale(d[uncertainty]));
        }

        const last = this.history[this.history.length-1];
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
        xScale = d3.scaleLinear().domain([0,max]).range([0,6]);

    popup.innerHTML=`Timestamp : ${timestamp.timestamp}<br>
      Contributor : ${timestamp.contributor}<br>
      <div class="content">
      <span>
        Imprecision uncertainty<br/>
        Incompleteness uncertainty<br/>
        Credibility uncertainty<br/>
        Ignorance uncertainty<br/>
        Variation uncertainty
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
        <span class="color variation" author="me" title="high" 
            style="width:${xScale(timestamp.variation)}em;" source="variation" cert="high"></span></br>
      </span>
      <span>
        ${timestamp.imprecision}</br> 
        ${timestamp.incompleteness}</br> 
        ${timestamp.ignorance}</br> 
        ${timestamp.credibility}</br>
        ${timestamp.variation}
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

function Model(){}

Model.prototype.expandedEmptyTag = function(empty_tag){
    const tag_name = empty_tag.slice(1).split(' ')[0],
        opening_tag = empty_tag.replace('/>','>'),
        closing_tag = '</'+tag_name+'>';

    return opening_tag + closing_tag;
}

Model.prototype.loadTEI = function(xml){
    return new Promise((resolve, error)=>{
        const sanityzed_xml = xml.replace(/\r/gm," "),
            ids_replaced_xml = xml.replace(/xml:id/gm,"id"),
            body_replaced_xml = ids_replaced_xml.replace(/body>/gm, 'page>'), // Creating a separate div would alter structure
            parsed_tei = $.parseXML(body_replaced_xml).documentElement,
            body = parsed_tei.getElementsByTagName('page')[0];
        
        this.TEItext = xml;
        this.TEIbody = body.innerHTML.replace(' xmlns="http://www.tei-c.org/ns/1.0"', '');
        this.TEIemptyTags = body.innerHTML.match(/<[^>]+\/>/gm);
        this.TEIheaderLength = xml.indexOf('<body>') + '<body>'.length;

        body.setAttribute('size', 'A4');
        $('#editor').html('');
        $('#editor').append(body);

        resolve(parsed_tei);
    });
}

/* Side panel
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 * */
function SidePanel(){
    this.shown = false;
    this.attributes = ['locus','cert','assertedValue','source'];
}
SidePanel.prototype.show = function(annotation, value, id){
    console.log(annotation)
    for(let attr of this.attributes){
        $('div#side-panel span#'+attr).text(' '+annotation.attributes[attr].value);
    }

    $('div#side-panel div#text').text(value);
    
    $('div#side-panel span.teiLegendElement').attr('id',id);
    $('div#side-panel span#parent').text(id);

    const text = document.getElementById('editor').textContent,
        exp = new RegExp(value,'g'),
        result = text.match(exp);
    $('div#side-panel div#tag-stats #times').text(' '+(result?result.length-1:0));

    const tags = Array.from(document.getElementsByTagName('certainty')).reduce((acd,c)=>acd+(c.textContent.includes(value)?1:0),0)
    $('div#side-panel div#tag-stats #tags').text(' '+(tags-1));
    $('div#side-panel div#certrange').attr('class',annotation.attributes['cert'].value)

    $('div#side-panel #value').text(value);

    const desc = Array.from(annotation.childNodes).filter(x=>x.nodeName.toLowerCase()=="desc");
    if(desc && desc.length >= 1)
        $('div#side-panel div#desc').html(
            `<b>Description :</b><br/><span>${desc[0].textContent}</span>`);
    else
        $('div#side-panel div#desc').html('');

    $('div#annotator-root').addClass('sidePanelDisplayed');
    this.shown = true;
}

SidePanel.prototype.hide = function(){
    $('div#annotator-root').removeClass('sidePanelDisplayed');
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

        $('section#top-panel #value').val(selection.text);   

        this.range = selection.range;
        this.selection = selection;
        this.show();
    }
}

Panel.prototype.createAnnotation = function(){
    if(this.selection == null)
        return

    const values = {};
    Array.from($("#top-panel input"), x=>x).map(i=>values[i.id]=i.value);
    Array.from($("#top-panel select"), x=>x).map(i=>values[i.id]=i.value);
    if(values['locus'] == 'value')
        values['value'] = values['value'];

    const annotation = (new Annotation()).fromDict(values);
    
    const url = API_urls.get_add_annotation_url(window.project, window.file);
    const data = {
            "start_pos": this.selection.abs_positions.start,
            "end_pos": this.selection.abs_positions.end,
            "asserted_value": "",
            "source": "",
            "locus": "",
            "certainty": "",
            "asserted_value": "",
            "description": "",
            "tag": values.proposedValue
        }

    if(getAnnotatorAttribute('annotation') == 'uncertainty'){
        Object.assign(data, {
            "source": values.source,
            "locus": values.locus,
            "certainty": values.cert,
            "asserted_value": values.proposedValue,
            "description": values.desc,
            "tag": ""
        });

        if(values['locus'] == 'attribute')
            data['attribute'] = values.attributeName;

        if(values['locus'] == 'name')
            data['tag'] = values.proposedValue;
    }
    
    $.ajax({
        url: url,
        type: 'PUT',   //type is any HTTP method
        contentType: "application/json; charset=UTF-8",
        data: JSON.stringify(data),      //Data as js object
        scriptCharset: 'utf8',
        success: function (xml) {
            console.log('annotate - success < ',xml);
            this.selection = null;
            $('input#selection').html('');
        },
        error: function(data) {
            console.log('annotate - error < ', data);
        }
    })
}

Panel.prototype.updateControls = function(annotationType, locus){
    if(annotationType == 'tei')
        $("#asserted-value-container").html($('#asserted-value-input-options [locus=name]')[0].outerHTML);
    else{
        const input = $('#asserted-value-input-options [locus='+locus+']')[0];
        $("#asserted-value-container").html(input.outerHTML);
    }
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

module.exports = { setup };
