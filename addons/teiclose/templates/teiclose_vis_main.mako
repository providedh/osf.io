<%inherit file="project/project_base.mako"/>
<%def name="title()">Close reading | ${file['filename']}</%def>

<%def name="stylesheets()">
    ${parent.stylesheets()}
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">
    <link rel="stylesheet" href="/static/css/pages/teiclose-page.css">
</%def>

## Use full page width
<%def name="container_class()">container-xxl</%def>

<div id="annotator-root" class="topPanelDisplayed" display-uncertainty='false' display-annotations='false' color-uncertainty='false' color-annotations='false'>
  <section id="toolbar">
    <div class="toolbarRow" id="toolbar-header">

      <div id="fileName">
        <div>
          <h2 class="break-word">
            ## Split file name into two parts: with and without extension
            <span id="fileTitleEditable">${ file['filename'] | h}</span>
            <a id='versionLink'  class='scripted'>(Version: ${ file['version'] | h})</a>
            % if file_revision:
              <small>&nbsp;${file_revision | h}</small>
            % endif
            
            <a id="saveFile">Save current file</a>
          </h2>
        </div>
        <div>
          <div id="toggleBar" class="pull-right"></div>
        </div>
      </div>
    </div>
    <div id="timeline">
        <div id="time-bar">
              <canvas></canvas>
              <hr/>
              <a id="toggle-timeline-details" title="show details for timeline" class='help'>( Show details )</a>
        </div>
        <div id="popup">
        </div>
    </div>
    <div class="toolbarRow" id="toolbar-controls">
      <div class="row" id="display-options">
        <span class="toolbar-control" id="">Display:
          <input id="display-uncertainty" type="checkbox" checked> Uncertainty 
          <input id="display-annotations" type="checkbox" checked> Annotations 
          <input id="display-legend" type="checkbox"> Legend
        </span>
        <span class="toolbar-control" id="">Use different colour for:
          <input id="color-uncertainty" type="checkbox" checked> Uncertainty types
          <input id="color-annotations" type="checkbox" checked> Annotation types
        </span>
      </div>
      <div class="row">
        <span class="toolbar-control" id="selected-control"> 
            <a id="openPanel" title="open panel" class='help'>( Open panel )</a>
        </span>
      </div>
    </div>
  </section>
  <section id="asserted-value-input-options">
    <input locus="attribute" type="text" class="input">
    <input locus="value" type="text" class="input">
    <select locus="name" class="input">
        <option value="date">Date</option>
        <option value="event">Event</option>
        <option value="geolocation">geolocation</option>
        <option value="name">Name</option>
        <option value="occupation">Occupation</option>
        <option value="object">Object</option>
        <option value="org">Org</option>
        <option value="person">Person</option>
        <option value="country">country</option>
        <option value="time">Time</option>
    </select>
  </section>
  <section id="top-panel" class="panel">
    <div class="toolbarRow" id="toolbar-controls">
      <div class="row">
        <span class="toolbar-control" id="annotation-options">
          <input type="radio" name="annotation" value="uncertainty" checked> Annotate Uncertainty
          <input type="radio" name="annotation" value="tei"> Annotate TEI
        </span>
      </div>
      <div class="row">
        <span class="toolbar-control" id="">
              Category of uncertainty <a title="help : category of the uncertainty" class='help'>?</a> 
              <select name="" id='category'>
                  <option class="ignorance" value="ignorance">Ignorance</option>
                  <option class="credibility" value="credibility">Credibility</option>
                  <option class="imprecision" value="imprecision">Imprecision</option>
                  <option class="incompleteness" value="incompleteness">Incompleteness</option>
              </select>
              Locus <a title="help : locus" class='help'>?</a>
              <select name="" id='locus'>
                  <option value="value">Value</option>
                  <option value="name">Name</option>
                  <option value="attribute">Attribute</option>
              </select>
                Tag name <a title="help : tag name" class='help'>?</a> 
                <select locus="name" id='tag-name'>
                  <option value="date">Date</option>
                  <option value="event">Event</option>
                  <option value="geolocation">geolocation</option>
                  <option value="name">Name</option>
                  <option value="occupation">Occupation</option>
                  <option value="object">Object</option>
                  <option value="org">Org</option>
                  <option value="person">Person</option>
                  <option value="country">country</option>
                  <option value="time">Time</option>
                </select>
              <span id="attribute-name-input"> 
                Attribute name <a title="help : attribute name" class='help'>?</a> <input type="text" id="attribute-name"> 
              </span>
        </span>
      </div>
      <div class="row">
        <span class="toolbar-control" id="">
          Text selection <a title="help : text selection" class='help'>?</a> <input type="text" name="" id="value" readonly> 
          Asserted value <a title="help : asserted value" class='help'>?</a> <span id="asserted-value-container"></span> 
          <span id="cert-input">
          Certainty <a title="help : certainty" class='help'>?</a> <select name="" id='cert'>
              <option value="unknown">Unknown</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
              </select>
          </span>    
        </span>
        <span>
          <button id="create-annotation">Create</button>
        </span>
      </div>
      <div class="row">
        <span class="toolbar-control" id="">
          <span id="references-container">
            References <a title="help : references" class='help'>?</a> 
            <div class="autocomplete">
              <input type="text" id="references-autocomplete"> 
              <input type="text" id="references"> 
            </div>
          </span>
          Description <a title="help : description" class='help'>?</a> <input type="text" id="desc"> 
        </span>
      </div>
      <div class="row closePanel">
          <a id="closePanel" title="close panel" class='help'>( Close panel )</a>
      </div>
    </div>
  </section>
  <div id="stats">
    Total annotations : <span id="annotations"> </span> 
    Total contributors : <span id="authors"> </span> 
    Date of editing : <span id="date"> </span>
  </div>
  <div class="legend" id="legend-right">
      <b>Annotation color scheme</b><br/>
      <span class="teiLegendElement" id="date">
          <span class="color" id=""></span> <i class="fas fa-calendar-alt"></i> Date
      </span>
      <span class="teiLegendElement" id="event">
        <span class="color" id=""></span> <i class="fas fa-calendar-check"></i> Event
      </span>
      <span class="teiLegendElement" id="location">
        <span class="color" id=""></span> <i class="fas fa-map-marked-alt"></i> Location, geolocation
      </span>
      <span class="teiLegendElement" id="name">
        <span class="color" id=""></span> <i class="fas fa-user-tag"></i> Name
      </span>
      <span class="teiLegendElement" id="occupation">
        <span class="color" id=""></span> <i class="fas fa-briefcase"></i> Occupation
      </span>
      <span class="teiLegendElement" id="object">
        <span class="color" id=""></span> <i class="fas fa-box"></i> Object
      </span>
      <span class="teiLegendElement" id="org">
        <span class="color" id=""></span> <i class="fas fa-building"></i> Org
      </span>
      <span class="teiLegendElement" id="person">
        <span class="color" id=""></span> <i class="fas fa-user"></i> Person
      </span>
      <span class="teiLegendElement" id="place">
        <span class="color" id=""></span> <i class="fas fa-map"></i> Place, country
      </span>
      <span class="teiLegendElement" id="time">
        <span class="color" id=""></span> <i class="fas fa-clock"></i> Time
      </span>
      <b>Uncertainty notion color scheme</b><br/>
      <span class="teiLegendElement">
        <span class="color uncertainty" author="me" title="unknown"
category="ignorance" cert="unknown"></span> 
        <span class="color uncertainty" author="me" title="low"
category="ignorance" cert="low"></span> 
        <span class="color uncertainty" author="me" title="medium" 
category="ignorance" cert="medium"></span> 
        <span class="color uncertainty" author="me" title="high" 
category="ignorance" cert="high"></span> 
        Ignorance
      </span>
      <span class="teiLegendElement">
        <span class="color uncertainty" author="me" title="unknown"
category="credibility" cert="unknown"></span> 
        <span class="color uncertainty" author="me" title="low"
category="credibility" cert="low"></span> 
        <span class="color uncertainty" author="me" title="medium"
category="credibility" cert="medium"></span> 
        <span class="color uncertainty" author="me" title="high" 
category="credibility" cert="high"></span> 
        Credibility
      </span>
      <span class="teiLegendElement">
        <span class="color uncertainty" author="me" title="unknown"
category="imprecision" cert="unknown"></span> 
        <span class="color uncertainty" author="me" title="low"
category="imprecision" cert="low"></span> 
        <span class="color uncertainty" author="me" title="medium"
category="imprecision" cert="medium"></span> 
        <span class="color uncertainty" author="me" title="high"
category="imprecision" cert="high"></span> 
        Imprecision
      </span>
      <span class="teiLegendElement">
        <span class="color uncertainty" author="me" title="unknown"
category="incompleteness" cert="unknown"></span>
        <span class="color uncertainty" author="me" title="low"
category="incompleteness" cert="low"></span> 
        <span class="color uncertainty" author="me" title="medium"
category="incompleteness" cert="medium"></span> 
        <span class="color uncertainty" author="me" title="high"
category="incompleteness" cert="high"></span> 
        Incompleteness
      </span>
  </div>
  <div  id="side-panel">
      <div id="text" class="row"></div>
      <div class="side-panel row">
          <b>Associated annotation : </b><span class="teiLegendElement" id=""><span class="color"></span></span><span id="parent"></span>
          <hr/>
          <div id="tag-stats" class="row">
              <b>Other occurencies in the text :</b><span id="times"></span><br/>
                <b>Other occurencies in  certainty tags :</b><span id="tags"></span>                
          </div>
          <hr/>
          <div id="annotation" class="row">
          <b>Locus :</b><span id="locus"></span></br>
          <b>Category of uncertainty :</b><span id="category"></span></br>
          <b>Certainty :</b>
          <div id="certrange">
                <span title="Unknown"></span>
                <span title="Low"></span>
                <span title="Medium"></span>
                <span title="High"></span>
            </div>
            <span id="cert"></span></br>
          <b>Value :</b><span id="value"></span></br>
          <b>Proposed value :</b><span id="assertedValue"></span></br>
          <span id="vis"></span>
          </div>
      </div>
      <div id="desc" class="row"></div>
  </div>
  <section id="editor">
  </section>
     <div id="close-reading-widget"></div>
</div>


<%def name="javascript_bottom()">
${parent.javascript_bottom()}
<script>
// Mako variables accessible globally
    window.contextVars = $.extend(true, {}, window.contextVars, {
        file: {
            id: ${ file['id'] | sjson, n },
            filename: ${ file['filename'] | sjson, n },
            provider: ${ file['provider'] | sjson, n },
            path: ${ file['path'] | sjson, n },
            addon_url: ${ file['addon_url'] | sjson, n },
            version: ${file['version'] | sjson, n }
        }
    });
</script>
<script src=${"/static/public/js/teiclose-page.js" | webpack_asset}></script>
</%def>
