<div class="modal fade" id="addTeiStatXPath">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
              <h3>Add XPath expression with an optional user-friendly name of it</h3>
            </div>

            <div class="modal-body">

                <div>
                    <div>
                        <div class="form-group">
                            <label for="xpath">XPath expression</label>
                            <input data-bind="value:xpath, event: { keyup: checkRequired }"
                                id="xpath"
                                type="text" required="required"
                                class="form-control xpath-expr"
                                placeholder='XPath expression' />
                            <br/>
                            <label for="name">Name</label>
                            <input data-bind="value:name"
                                id="name"
                                type="text"
                                class="form-control xpath-name"
                                placeholder='Optional name' />
                        </div>
                        <div class="help-block">
                            <p class="text-danger" data-bind="html: message, attr: {class: messageClass}"></p>
                        </div>
                    </div>

                </div>

            </div><!-- end modal-body -->

            <div class="modal-footer">

                <a href="#" class="btn btn-default" data-dismiss="modal">Cancel</a>
                <a class="btn btn-primary" data-bind="click:submit, css:{disabled: disableSubmit}, text: submitText"></a>

            </div><!-- end modal-footer -->
        </div><!-- end modal-content -->
    </div><!-- end modal-dialog -->
</div><!-- end modal -->
