jQuery.noConflict();

function GSInviteByCSVOptionalAttributes(tableSelector, optionalMenuSelector) {
    var table=null, labels=null, titles=null, examples=null, optionalMenu=null;

    function get_most_recent_optional_column_label() {
        var lastLabel=null;
        lastLabel = table.find('.labels .col-label:last .val');
        return lastLabel.text();
    }

    function new_label_cell(id, label) {
        var retval=null, btn=null;
        retval = jQuery('<th class="slide col-label optional '+
                        id+'" data-menu-item="'+id+'"> </th>');
        retval.append(jQuery('<span class="val">'+label+'</span>'));
        retval.append('&#160;');
        btn = jQuery('<a class="muted small">(remove)</a>');
        btn.click(column_remove_clicked);
        retval.append(btn);
        return retval
   }

    function colgroup_span_incr(val) {
        var cg=null;
        cg = jQuery('#gs-group-member-invite-csv-columns-optional');
        cg.attr('span', (parseInt(cg.attr('span'))+val).toString());
    }

    function add_column(id, name) {
        var newColLabel=null, btn=null, newColLabel=null
            label=null, title=null, example=null;
        oldColLabel = get_most_recent_optional_column_label();
        newColLabel = String.fromCharCode(oldColLabel.charCodeAt(0) + 1);

        label = new_label_cell(id, newColLabel);
        // The Add-selector is actually the last cell in the row.
        labels.find('td:last').before(label);

        title = jQuery('<td class="slide '+id+'">'+name+'</td>');
        titles.find(':last').after(title);

        example = jQuery('<td class="muted slide '+id+'">Example '
                         +name+'</td>');
        examples.find(':last').after(example);

        colgroup_span_incr(1);
        get_properties_from_cells();
    }

    function menu_option_clicked(event) {
        var t=null, id=null, name=null;
        t = jQuery(event.target);
        if (!t.parent().hasClass('disabled')) {
            id = t.attr('id');
            name = t.text()
            add_column(id, name);
            t.parent().addClass('disabled');
        }
    }

    function del_col(index) {
        var i=null;
        i = index.toString();
        labels.find('th:nth-child('+i+')').remove();
        titles.find(':nth-child('+i+')').remove();
        examples.find(':nth-child('+i+')').remove();
    }

    function column_remove_clicked (event) {
        var t=null, cell=null, menuItemId=null, menuItem=null, row=null,
            i=null;

        t = jQuery(event.target);
        cell = t.parent('th');

        menuItemId = cell.attr('data-menu-item');
        menuItem = jQuery('#'+menuItemId);
        menuItem.parent().removeClass('disabled');

        row = jQuery('.col-label');
        i = row.index(cell)+2;
        del_col(i);

        colgroup_span_incr(-1);
        relabel_columns();
    }

    function relabel_columns() {
        jQuery('.col-label .val').each(function(i, l) {
            var label=null, newColLabel = null;
            label = jQuery(l);
            newColLabel = String.fromCharCode(65 + i);
            label.text(newColLabel);
        });
    }

    function get_properties_from_cells() {
        var cells=null, retval=null;
        cells = table.find('.col-label');
        retval = jQuery.map(cells, function(c, i){
            var r=null;
            r = jQuery(c).attr('data-menu-item');
            return r
        });
        return retval;
    }

    function get_titles_from_cells() {
        var cells=null, retval=null;
        cells = table.find('.col-label');
        retval = jQuery.map(cells, function(c, i){
            var id=null, r=null;
            id = jQuery(c).attr('data-menu-item');
            r = titles.find('.'+id).text();
            return r
        });
        return retval;
    }

    function get_egs_from_cells() {
        var cells=null, retval=null;
        cells = table.find('.col-label');
        retval = jQuery.map(cells, function(c, i){
            var id=null, r=null;
            id = jQuery(c).attr('data-menu-item');
            r = examples.find('.'+id).text();
            return r
        });
        return retval;
    }

    function init() {
        optionalMenu = jQuery(optionalMenuSelector);
        optionalMenu.find('a')
            .removeAttr('href')
            .click(menu_option_clicked);

        table = jQuery(tableSelector);
        labels = table.find('.labels');
        titles = table.find('.titles');
        examples = table.find('.examples');
    }
    init();  // Note: automatic execution

    return {
        get_properties: function () {
            return get_properties_from_cells();
        },
        get_titles: function() {
            return get_titles_from_cells();
        },
        get_examples: function() {
            return get_egs_from_cells();
        }
    }
}

function TemplateGenerator(attributes) {
    var URL='data:text/csv;charset=utf-8,';

    function array_to_row(arr) {
        var retval=null;
        retval = jQuery.map(arr, function(v, i) {
            return '"'+v+'"';
        }).join(',');
        return retval;
    }

    function header_row() {
        var titles=null, retval=null;
        titles = attributes.get_titles();
        retval = array_to_row(titles);
        return retval;
    }

    function example_row() {
        var egs=null, retval=null;
        egs = attributes.get_examples();
        retval = array_to_row(egs);
        return retval;
    }

    return {
        generate: function () {
            var s=null,a=null;
            s = URL + encodeURI(header_row()+'\n'+example_row());
            // Thanks to <http://stackoverflow.com/questions/17836273/>
            // For some this fails with jQuery, so do it ol' skool.
            a = document.createElement('a');
            a.href = s;
            a.style = 'display:none;';
            a.target = '_blank';
            a.download = 'template.csv';
            document.body.appendChild(a);
            a.click();
        }
    }
}

function ParserAJAX (attributes, formSelector, feedbackSelector, 
                     checkingSelector) {
    var form=null, feedback=null, checking=null,
        URL='csv.json', PARSE_SUCCESS='parse_success', PARSE_FAIL='parse_fail';

    function success (data, textStatus, jqXHR) {
        var e=null, json=null;
        checking.find('.loading')
            .removeClass('loading')
            .attr('data-icon', '\u2714');
        if (data.status == -3) {
            e = jQuery.Event(PARSE_FAIL);
            checking.trigger(e);
        } else {
            e = jQuery.Event(PARSE_SUCCESS);
            checking.trigger(e, [data]);
        }
    }

    function error(jqXHR, textStatus, errorThrown) {
        
    }

    function show_feedback() {
        var csvFile=null, name=null;

        form.removeClass('in');
        feedback.addClass('in');

        csvFile = document.getElementById('form.file').files[0];
        name = csvFile.name;
        feedback.find('.filename').text(name);

        checking.addClass('in');
    }

    function send_request() {
        var attributeIds=null, d=null, csvFile=null, settings=null;
        // To be able to submit a file (sanely) using AJAX we have to
        // use a FormData object and a File object. Because of this the
        // page requires HTML5: Chrome 13, Firefox 7, IE 10, Opera 16, and
        // Safari 6
        // <https://developer.mozilla.org/en-US/docs/Web/API/FormData>
        // <https://developer.mozilla.org/en-US/docs/Web/API/File>
        d = new FormData();
        csvFile = document.getElementById('form.file').files[0];
        d.append('csv', csvFile);

        attributeIds = attributes.get_properties();
        jQuery.each(attributeIds, function(i, attr) {
            // 'columns' is appended multiple times because it is a list.
            d.append('columns', attr);
        });

        // The ID of the button that was "clicked", for zope.formlib
        d.append('submit', '');

        // The following is *mostly* a jQuery.post call:
        // jQuery.post(URL, d, success, 'application/json');
        settings = {
            accepts: 'application/json',
            async: true,
            cache: false,
            contentType: false,
            crossDomain: false,
            data: d,
            dataType: 'json',
            error: error,
            headers: {},
            processData: false,  // No jQuery, put the data down.
            success: success,
            traditional: true,
            // timeout: TODO, What is the sane timeout?
            type: 'POST',
            url: URL,
        };
        jQuery.ajax(settings);
    }

    function init() {
        form = jQuery(formSelector);
        feedback = jQuery(feedbackSelector);
        checking = jQuery(checkingSelector);
    }
    init();  // Note: automatic execution

    return {
        parse: function(callback) {
            show_feedback();
            send_request();
        },
        'SUCCESS_EVENT': PARSE_SUCCESS,
        'FAIL_EVENT': PARSE_FAIL
    }
}


function InviterAJAX (invitingBlockSelector) {
    var invitingBlock=null, progressBar=null, currN=null, total=null,
        success=null, ignored=null, problems=null, email=null,
        json=null, membersToInvite=null, totalRows=0, currRow=0,
        URL='gs-group-member-invite-json.html'

    function show_inviting() {
        invitingBlock.addClass('in');
        email.text('');
        total.text(totalRows.toString());
        currN.text('0');
        progressBar.css('width', '0%');

        success.removeClass('in');
        ignored.removeClass('in');
        problems.removeClass('in');
    }

    function error (jqXHR, textStatus, errorThrown) {
        var info=null;
        console.log('Issues');
        console.log(textStatus);
        console.error(errorThrown);
        info = '<li>Problem with row ' + currRow.toString() + ': ' 
            + textStatus + '</li>';
        log_feedback(info, problems);
        next();
    }

    function log_feedback(info, area) {
        area.find('ul').append(info);
        if (!area.hasClass('in')) {
            area.addClass('in');
        }
    }

    function next() {
        if (membersToInvite.length == 0) {
            done();
        } else {
            invite_member();
        }
    }

    function invite_success (data, textStatus, jqXHR) {
        var info='';
        // "Success" is broadly defined as "not an AJAX error".
        info = '<li>' + data.message[0] + '</li>';
        if (data.status == 3) { // Existing member
            log_feedback(info, ignored);
        } else if ((data.status == 2) || (data.status == 1)) {
            log_feedback(info, success);
        } else { // Assume it is a problem
            info = jQuery(info);
            info.prepend('<strong>Row ' + currRow.toString() + ': </strong>');
            log_feedback(info, problems);
        }
        next();
    }
    function invite_member() {
        // SIDE EFFECT: Reduces the length of membersToInvite by one
        var pc=0, memberToInvite=null, settings=null, d=null, attr=null;

        currRow++;
        currN.text(currRow.toString());
        // The "+ 1" is so the progress bar is incomplete when processing the
        // final row.
        pc = (currRow / (totalRows + 1.0)) * 100;
        progressBar.css('width', pc.toString()+'%')
        
        memberToInvite = membersToInvite.pop();
        email.text(memberToInvite.email);  // Email must exist
        // The invite code is actually expecting a toAddr field, rather than
        // email, so rename the property.
        memberToInvite['toAddr'] = memberToInvite.email;
        delete memberToInvite.email ;

        d = new FormData();
        for (attr in memberToInvite) {
            d.append(attr, memberToInvite[attr])
        }
        d.append('subject', 'Invite');  // TODO: sort out the message
        d.append('message', 'Stuff');  // TODO: sort out the message
        d.append('fromAddr', 'mpj17@onlinegroups.net');  // TODO from address
        d.append('delivery', 'email');  // TODO: delivery
        // The ID of the button that was "clicked", for zope.formlib
        d.append('submit', 'submit');

        settings = {
            accepts: 'application/json',
            async: true,
            cache: false,
            contentType: false,
            crossDomain: false,
            data: d,
            dataType: 'json',
            error: error,
            headers: {},
            processData: false,
            success: invite_success,
            traditional: true,
            // timeout: TODO, What is the sane timeout?
            type: 'POST',
            url: URL,
        };
        jQuery.ajax(settings);
    }

    function done () {
        var m=null;
        progressBar.css('width', '100%');
        invitingBlock.find('.loading')
            .removeClass('loading')
            .attr('data-icon', '\u2714');
        m = 'Processed ' + totalRows.toString() + ' people in '+
            (totalRows + 1).toString() + ' rows. ' +
            '(The first row was presumed to be a header and ignored.)'
        invitingBlock.find('.current-operation').text(m);
    }

    function init () {
        invitingBlock = jQuery(invitingBlockSelector);
        progressBar = invitingBlock.find('.bar');
        total = invitingBlock.find('.total');
        email = invitingBlock.find('.curr-email');
        currN = invitingBlock.find('.curr-n');
        success = invitingBlock.find('.success');
        ignored = invitingBlock.find('.ignored');
        problems = invitingBlock.find('.problems');
    }
    init();  // Note: automatic execution.

    function set_member_data(jsonData) {
        json = jsonData;
        // Because pop() pops from the end we reverse the list so
        // people are processed in the same order as the CSV.
        json.reverse();
        membersToInvite = json.slice(0);  // Copy the list
        totalRows = json.length;
    }

    return {
        invite: function (e, jsonData) {
            set_member_data(jsonData)
            show_inviting();
            invite_member();
        }
    }
}

jQuery(window).load(function () {
    var ms=null, ts=null, attributes=null, templateGenerator=null,
        parser=null, inviter=null;

    ms = '.dropdown-menu';
    ts = '#gs-group-member-invite-csv-columns-table';
    attributes = GSInviteByCSVOptionalAttributes(ts, ms);

    templateGenerator = TemplateGenerator(attributes);
    jQuery('#gs-group-member-invite-csv-columns-template .btn')
        .click(templateGenerator.generate);

    parser = ParserAJAX(attributes, '#gs-group-member-invite-csv-form',
                        '#gs-group-member-invite-csv-feedback',
                        '#gs-group-member-invite-csv-feedback-checking');
    jQuery('#form\\.actions\\.invite').click(parser.parse);

    inviter = InviterAJAX('#gs-group-member-invite-csv-feedback-inviting',
                          '#gs-group-member-invite-csv-feedback-inviting .bar')
   jQuery('#gs-group-member-invite-csv-feedback-checking')
        .on(parser.SUCCESS_EVENT, inviter.invite);
});
