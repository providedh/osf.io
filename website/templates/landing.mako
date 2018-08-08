## -*- coding: utf-8-*-
<%inherit file="base.mako"/>

<%def name="title()">Home</%def>

<%def name="content_wrap()">
    <div class="watermarked">
            % if status:
                <%include file="alert.mako" args="extra_css='alert-front text-center'"/>
            % endif
            ${self.content()}
    </div><!-- end watermarked -->
</%def>

<%def name="content()">

    <!-- Main jumbotron for a primary marketing message or call to action -->
    <div id="home-hero">
      <div class="container text-center">
        <div class="visible-xs-block network-bg"></div>
        <div id="canvas-container">
          <canvas id="demo-canvas"></canvas>
        </div>

        <div id="logo">
          <img src="/static/img/providedh-logo.svg"/>
        </div>
        
        <h1 class="hero-brand">Collaborative Platform Prototype</h1>
                  
      </div>
    </div>

    <div class="container grey-pullout space-top space-bottom">

      <div class="row space-bottom">
        <div class="col-xs-12 text-center">
          <h2><strong>PRO</strong>gressive <strong>VI</strong>sual <strong>DE</strong>cision-Making in <strong>D</strong>igital <strong>H</strong>umanities</h2>
        </div>
      </div>

      <div class="row feature-1">
        <div class="col-md-6">
          <div class="row">
            <div class="col-xs-1">
              <i class="icon"></i>
            </div>
            <div class="col-xs-9 col-xs-offset-1">
              <h3>Uncertainty in digital humanities</h3>
              <p>Explore the completeness and evolution of digital research objects <strong>in terms of the degree of uncertainty</strong>, and share perspectives and insights with other stakeholders of society. <span class="label label-primary">Metrics of Uncertainty</span></p>
            </div>
          </div>
          <div class="row">
            <div class="col-xs-1">
              <i class="icon"></i>
            </div>
            <div class="col-xs-9 col-xs-offset-1">
              <h3>Progressive visualizations</h3>
              <p>Incorporate <strong>visualizations that allow the correct interpretation</strong> of the concepts of accuracy and precision in your data. <span class="label label-primary">Progressive Visual Analysis</span></p>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="row">
            <div class="col-xs-1">
              <i class="icon"></i>
            </div>
            <div class="col-xs-9 col-xs-offset-1">
              <h3>Structured projects</h3>
              <p>Keep all your files and data in <strong>one centralized location.</strong> No more trawling emails to find files or scrambling to recover from lost data. <span class="label label-primary">Secure Cloud</span></p>
            </div>
          </div>
          <div class="row">
            <div class="col-xs-1">
              <i class="icon"></i>
            </div>
            <div class="col-xs-9 col-xs-offset-1">
              <h3>Control access</h3>
              <p><strong>You control which parts of your project are public or private</strong> making it easy to collaborate with the worldwide community or just your team. <span class="label label-primary">Project-level Permissions</span></p>
            </div>
          </div>
        </div>
      </div>

    </div>

    <div class="space-top space-bottom feature-6">
    </div>

</%def>

<%def name="footer()">
    <%include file="footer.mako"/>
</%def>

<%def name="stylesheets()">
    ${parent.stylesheets()}
    <link rel="stylesheet" href="/static/css/pages/landing-page.css">
    <link rel="stylesheet" href="/static/css/front-page.css">
</%def>

<%def name="javascript_bottom()">
    ${parent.javascript_bottom()}
    <script src=${"/static/public/js/landing-page.js" | webpack_asset}></script>
    %if recaptcha_site_key:
        <script src="https://recaptcha.net/recaptcha/api.js" async defer></script>
    %endif
</%def>
