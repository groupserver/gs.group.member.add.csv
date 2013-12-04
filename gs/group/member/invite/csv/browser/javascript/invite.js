jQuery.noConflict();

function GSInviteByCSVOptionalAttributes(tableSelector, optionalMenuSelector) {
    var table=null, labels=null, titles=null, examples=null, optionalMenu=null;

    function get_most_recent_optional_column_label() {
        var lastLabel=null;
        lastLabel = table.find('.labels .col-label:last');
        return lastLabel.text();
    }

    function new_label_cell(id, label) {
        var retval=null, btn=null;
        retval = jQuery('<th class="slide col-label '+id+'" data-menu-item="'+
                       id+'">'+label+' </th>');
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
        id = t.attr('id');
        name = t.text()
        add_column(id, name);

        t.parent().addClass('disabled');
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

function ParserAJAX (attributes) {
    return {
        parse: function(callback) {
            var attributeIds=null;
            attributeIds = attributes.get_properties();
            console.log(attributeIds);
        }
    }
}

jQuery(window).load(function () {
    var ms=null, ts=null, attributes=null, templateGenerator=null,
    parser=null;

    ms = '.dropdown-menu';
    ts = '#gs-group-member-invite-csv-columns-table';
    attributes = GSInviteByCSVOptionalAttributes(ts, ms);

    templateGenerator = TemplateGenerator(attributes);
    jQuery('#gs-group-member-invite-csv-columns-template .btn')
        .click(templateGenerator.generate);

    parser = ParserAJAX(attributes);
    jQuery('#form\\.actions\\.invite').click(parser.parse);
});
