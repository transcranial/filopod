/*!
 * Copyright (c) 2013 Filopod, LLC
 *
 * http://www.filopod.com
 */

$(function() {

function get_search_query() {
    return $('#searchbox input').val();
}

function get_respacks() {
    return $('#respacks').attr('code');
}

function get_numnodes() {
    return $('#node_number').attr('code');
}

function get_concept_types_code() {
    return $('#category_filter').attr('code');
}

function get_assoc_measure() {
    return $('#assoc_measure').attr('code');
}

function activateSearch() {
    $('#concept_nodes').hide();
    $('#search_selection_content').html("");
    $('#search_selection').show();
    $('#search_selection_spinner').show();
    $('#options_panel').hide();
    // google analytics event tracking
    _gaq.push(['_trackEvent', 'concept_search', 'search', get_search_query()]);
    $.get('/get_search_concepts', 
        {
            query: get_search_query(),
            respacks_code: get_respacks()
        }, 
        function(data) {
            $('#search_selection_spinner').hide();
            if (data['concepts'].length == 0) {
                $('#search_selection_content').html("<div class='alert alert-danger'>Query did not match any concepts. Search again. (note: resource collection may not contain any references to query)</div>");
            } else if (data['concepts'].length == 1) {
                $('#searchbox input').val("");
                $('#search_selection').hide();
                var terms_string = "";
                $.each(data['terms'][0], function(j, term) {
                        terms_string += ("[" + term + "] ");
                    });
                displayConceptNodes(data['concept_ids'][0], data['concepts'][0], terms_string);
            } else {
                $('#search_selection_content').html("");
                var html_string = "<h3>Choose from among the following:</h3>";
                // data is json format
                $.each(data['concepts'], function(i, concept) {
                    if (i % 3 == 0) { 
                        html_string += "<div class='row'>";
                    }
                    html_string += "<div class='col-md-4'>";
                    html_string += ("<span class='source-concept' concept_id='" + data['concept_ids'][i] + "'>" + concept + "</span><br><br>");
                    html_string += ("<span class='source-terms' data-toggle='tooltip' data-original-title='");
                    $.each(data['terms'][i], function(j, term) {
                        html_string += ("[" + term + "] ");
                    });
                    html_string += ("'>[ terms contained ]</span>");
                    html_string += "</div>";
                    if (i % 3 == 2 || i == data['concepts'].length - 1) {
                        html_string += "</div>";
                    }
                });
                $('#search_selection_content').append(html_string);
                $('.source-terms')
                    .tooltip({
                        placement: 'top',
                        trigger: 'hover'
                    });
                $('#search_selection [class*="col-"]').click(function(e) {
                    $('#searchbox input').val("");
                    $('#search_selection').hide();
                    var source_concept_id = $(this).children('.source-concept').attr('concept_id');
                    var source_concept_name = $(this).children('.source-concept').text();
                    // google analytics event tracking
                    _gaq.push(['_trackEvent', 'concept_search', 'select', source_concept_name]);    
                    displayConceptNodes(source_concept_id, source_concept_name, $(this).children('.source-terms').attr('data-original-title'));
                });
            }
            compressSearchPanel();
		}
    );
}

function expandSearchPanel() {
    var verticalPad = 0.5 * ($(window).innerHeight() - $('#main .container').outerHeight(true) - $('footer').outerHeight(true) - $('header').outerHeight(true));
    $('#main')
        .stop()
        .animate({
            paddingTop: verticalPad,
            paddingBottom: verticalPad
        }, 1000, 'easeOutCirc');
}

function compressSearchPanel() {
    $('#main')
        .stop()
        .animate({
            paddingTop: 20,
            paddingBottom: 20
        }, 800, 'easeOutCirc');
}

function loadRespacksGroup() {
    var respacks_code = $('#respacks').attr('code');
    $('#respacks button').each(function(i) {
        $(this).click(function() {
            $(this).toggleClass('active');
            var respacks_code = "";
            $('#respacks button').each(function() {
                if ($(this).hasClass('active')) {
                    respacks_code += "1";
                    $(this).children('span').addClass('glyphicon-ok');
                    $(this).children('span').removeClass('glyphicon-remove');
                } else {
                    respacks_code += "0";
                    $(this).children('span').removeClass('glyphicon-ok');
                    $(this).children('span').addClass('glyphicon-remove');
                }
            });
            $('#respacks').attr('code', respacks_code);
        });
        if (respacks_code[i] == '1') {
            $(this).addClass('active');
            $(this).children('span').addClass('glyphicon-ok');
            $(this).children('span').removeClass('glyphicon-remove');
        } else {
            $(this).removeClass('active');
            $(this).children('span').removeClass('glyphicon-ok');
            $(this).children('span').addClass('glyphicon-remove');
        }
    });
}

function loadCatFilterGroup() {
    var code_all = $('#category_filter').attr('code');
    $('#category_filter .css-checkbox').each(function() {
        if (code_all.indexOf($(this).attr('code')) !== -1) {
            $(this).prop('checked', true);
        }
    });
    $('#category_filter .css-checkbox').change(function(e) {
        var code = "";
        $('#category_filter .css-checkbox').each(function() {
            if ($(this).prop('checked')) {
                code = code + $(this).attr('code');
            }
        });
        $('#category_filter').attr('code', code);
    });
}

function displayConceptNodes(concept_id, concept_name, concept_terms) {
    $('#concept_nodes').show();
    $('#concept_nodes_heading').html("");
    var html_string = "";
    html_string += ("<div id='source-concept-div'><span class='source-concept' concept_id='" + concept_id + "'>" + concept_name + "</span></div>");
    html_string += ("<div id='source-terms-div'><span class='source-terms' data-toggle='tooltip' data-original-title='" + concept_terms + "'>[ terms contained ]</span></div>");
    $('#concept_nodes_heading').append(html_string);
    $('.source-terms')
        .tooltip({
            placement: 'bottom',
            trigger: 'hover'
        });
    updateNodes(concept_id);
}

function updateNodes(concept_id) {
    $('#concept_nodes_spinner').show();
    $('#options_button').hide();
    $('#concept_nodes_content').html("");
    $.get('/get_concept_nodes', 
        {
            concept_id: concept_id,
            respacks_code: get_respacks(),
            numnodes: get_numnodes(),
            concept_types_code: get_concept_types_code(),
            assoc_measure: get_assoc_measure()
        }, 
        function(data) {
            $('#concept_nodes_spinner').hide();
            $('#options_button').show();
            $.each(data['nodesName'], function(i, nodeName) {
                var html_string = "";
                html_string += "<div class='row target-concept-div' concept_id='" + data['nodesIndex'][i] + "'>";
                html_string += "<div class='col-md-3 target-concept-div-left'>";
                html_string += "<div class='target-concept' concept_id='" + data['nodesIndex'][i] + "'>" + nodeName + "</div>";
                var terms_string = "";
                $.each(data['nodesTerms'][i], function(j, term) {
                        terms_string += ("[" + term + "] ");
                    });
                html_string += "<span class='make_source_concept'>[ make primary concept ]</span>&nbsp;&nbsp;<span class='target-terms' data-toggle='tooltip' data-original-title='" + terms_string + "'>[ terms contained ]</span>";
                html_string += "<div class='target-concept-img'><img title='image provided by Bing' src='" + concept_images_path + data['nodesIndex'][i] + ".jpg' /></div>";
                html_string += "<div class='values-bar-div'><span class='values-label'>association strength: " + data['nodesValue'][i] + "%</span><div class='values-bar' style='width:" + data['nodesValue'][i] + "%;'></div></div>";
                html_string += "</div>"; //class='col-md-3 target-concept-div-left'
                html_string += "<div class='col-md-9 target-concept-div-right'>";
                html_string += "<div class='jcarousel'><ul></ul></div>";
                html_string += "</div>"; //class='col-md-9 target-concept-div-right'
                html_string += "</div>"; //class='row target-concept-div'
                $('#concept_nodes_content').append(html_string);
                $('.target-concept-div[concept_id="' + data['nodesIndex'][i] + '"] .make_source_concept').click(function() {
                    // google analytics event tracking
                    _gaq.push(['_trackEvent', 'concept_nav', 'new_source', nodeName]);
                    displayConceptNodes(data['nodesIndex'][i], nodeName, terms_string);
                });
            });
            $('.target-terms')
                .tooltip({
                    placement: 'right',
                    trigger: 'hover'
                });
            $('.target-concept-div-right').each(function() {
                $(this).height($(this).siblings('.target-concept-div-left').height());
            });
            activateCarousels(concept_id);
            $('html,body').animate({scrollTop: $('#concept_nodes').offset().top - 5}, 800, 'easeOutCirc');
		}
    );
}

function activateCarousels(concept_id) {
    
    function initItems(parent_div, loadingCaPanel_el) {
        var el = parent_div;
        var current_page = 0;
        var has_next = false;
        // google analytics event tracking
        _gaq.push(['_trackEvent', 'fetch_resources', 'fetch']);
        $.get('/fetch_resources',
            {
                respacks_code: get_respacks(),
                source_concept_id: concept_id,
                target_concept_id: el.attr('concept_id'),
                page: 1
            },
            function(data) {
                current_page = data['current_page'];
                has_next = data['has_next'];
                el.find('.jcarousel')
                    .jcarousel({
                        animation: {
                            duration: 800,
                            easing: 'easeOutExpo',
                            complete: function() {
                            }
                        }
                    });
                appendItems(data, el, 0);
                el.children('.target-concept-div-right').append("<div class='jcarousel-control-prev'> </div><div class='jcarousel-control-next'> </div>");
                el.children('.target-concept-div-right').children('.jcarousel-control-prev')
                    .on('jcarouselcontrol:active', function() {
                        $(this).css('visibility','visible');
                        $(this).addClass('jcarousel-control-bounce-left');
                    })
                    .on('jcarouselcontrol:inactive', function() {
                        $(this).css('visibility','hidden');
                        $(this).removeClass('jcarousel-control-bounce-left');
                    })
                    .jcarouselControl({
                        target: '-=1'
                    });
                el.children('.target-concept-div-right').children('.jcarousel-control-next')
                    .on('jcarouselcontrol:active', function() {
                        $(this).css('visibility','visible');
                        $(this).addClass('jcarousel-control-bounce-right');
                    }).on('jcarouselcontrol:inactive', function() {
                        $(this).css('visibility','hidden');
                        $(this).removeClass('jcarousel-control-bounce-right');
                    }).jcarouselControl({
                        target: '+=1'
                    }).on('click', function() {
                        var num_snippets_before_fetching = 5; // number of snippets to go before dynamically fetching additional snippets
                        var current_snippet_num = parseInt(el.find('.jcarousel').jcarousel('target').attr('snippet_num'));
                        var last_snippet_num = parseInt(el.find('.jcarousel li').last().attr('snippet_num'));
                        if((last_snippet_num - current_snippet_num) == num_snippets_before_fetching && has_next) {
                            $.get('/fetch_resources',
                                {
                                    respacks_code: get_respacks(),
                                    source_concept_id: concept_id,
                                    target_concept_id: el.attr('concept_id'),
                                    page: current_page + 1
                                },
                                function(data_new) {
                                    current_page = data_new['current_page'];
                                    has_next = data_new['has_next'];
                                    appendItems(data_new, el, last_snippet_num);
                                }
                            );
                        }
                    });
                // remove loading indicator panel when initialization complete
                loadingCaPanel_el.remove();
            }
        );
    }

    function appendItems(data, parent_div, last_subres_num) {
        var el = parent_div;
        var concept_id = el.attr('concept_id');
        $.each(data['subresources_paginated'], function(subres_i, subresource) {
            var snippet_num = last_subres_num + subres_i + 1;
            var snippet_details_string = "";
            snippet_details_string += "<p align=left>";
            snippet_details_string += "Snippet " + snippet_num.toString() + " of " + data['subresources_totnum'].toString() + "<br><br>";
            if(subresource.name) { snippet_details_string += "(<i>" + subresource.name + "</i>) "; }
            var resource = data['resources_paginated'][subres_i];
			if(resource.title) { snippet_details_string += resource.title + ". "; }
			if(resource.author) { snippet_details_string += resource.author + ". "; }
			if(resource.journal) { snippet_details_string += "<i>" + resource.journal + "</i>. "; }
			if(resource.volume) { snippet_details_string += "vol. " + resource.volume + ". "; }
			if(resource.issue) { snippet_details_string += "(" + resource.issue + ") "; }
			if(resource.firstpage & resource.lastpage) { snippet_details_string += "p." + resource.firstpage + "-" + resource.lastpage + ". "; }
			if(resource.date) { snippet_details_string += resource.date + ". "; }
            snippet_details_string += "</p>";
            var items_list = "";
            var figure_info = "";
            if(subresource.url) { // if snippet is figure, add link to view figure
                figure_info = "<span id='concept-" + concept_id.toString() + "-snippet-" + snippet_num.toString() + "-figure' class='figure-open'><img src='" + images_path + "photo.png' />&nbsp;&nbsp;Open figure</span><br><br>";
            }
            items_list += "<li id='concept-" + concept_id.toString() + "-snippet-" + snippet_num.toString() + "' snippet_num='" + snippet_num.toString() + "'>";
            items_list += "<div class='snippet-container'>" + figure_info + subresource.snippet + "</div>";
            //if(!(subresource.url)) { // if snippet is paragraph, not figure
                items_list += "<div class='snippet-expand'><span id='concept-" + concept_id.toString() + "-snippet-expand-" + snippet_num.toString() + "'>Expand to paragraph</span></div>";
            //}
            items_list += "<div class='snippet-links'>";
            items_list += "<span class='snippet-info' data-toggle='tooltip' data-original-title='" + snippet_details_string + "'>[ snippet details ] </span>";
            items_list += "<a href='http://www.ncbi.nlm.nih.gov/pubmed/?term=" + data['resources_paginated'][subres_i].identifier + "' target='_blank'>Pubmed link</a>";
            items_list += "<a href='" + data['resources_paginated'][subres_i].url + "' target='_blank'>Direct link</a>";
            items_list += "</div></li>";
            el.children('.target-concept-div-right').children('.jcarousel').children('ul').append(items_list);
            // sets up snippets as custom scrollable
            $('#concept-' + concept_id.toString() + '-snippet-' + snippet_num.toString() + ' .snippet-container')
                .mCustomScrollbar({
                    theme: 'custom-dark-thin',
                    scrollButtons: {
                        enable: false
                    }
                });
            // activate snippet-info tooltip
            $('#concept-' + concept_id.toString() + '-snippet-' + snippet_num.toString() + ' .snippet-info')
                .tooltip({
                    placement: 'top',
                    trigger: 'hover', 
                    container: 'body',
                    html: 'true'
                });
            if(subresource.url) { // if snippet is figure, create popup to view figure
                $('#concept-' + concept_id.toString() + '-snippet-' + snippet_num.toString() + '-figure').click(function() {
                    var expanded = "";
                    expanded += "<div id='concept-" + concept_id.toString() + "-expanded-popup-" + snippet_num.toString() + "-figure' class='expanded-popup-figure'><span class='b-close'><span>x</span></span>";
                    expanded += "<img src='" + subresource.url + "' />";
                    expanded += "</div>";
                    $('body').append(expanded);
                    $('#concept-' + concept_id.toString() + '-expanded-popup-' + snippet_num.toString() + '-figure')
                        .bPopup({
                            positionStyle: 'fixed',
                            modalColor : '#000',
                            opacity: 0.8,
                            easing: 'easeInOutExpo', //uses jQuery easing plugin
                            speed: 400,
                            transition: 'slideDown',
                            onClose: function() { 
                                $('#concept-' + concept_id.toString() + '-expanded-popup-' + snippet_num.toString() + '-figure').remove(); 
                            }
                        });
                });
            }
            //if(!(subresource.url)) { // if snippet is paragraph, not figure
                $('#concept-' + concept_id.toString() + '-snippet-expand-' + snippet_num.toString()).click(function() {
                    var expanded = "";
                    expanded += "<div id='concept-" + concept_id.toString() + "-expanded-popup-" + snippet_num.toString() + "' class='expanded-popup'><span class='b-close'><span>x</span></span>";
                    expanded += "<div class='expanded-popup-content'>" + subresource.content + "</div>";
                    expanded += "</div>";
                    $('body').append(expanded);
                    $('#concept-' + concept_id.toString() + '-expanded-popup-' + snippet_num.toString())
                        .bPopup({
                            positionStyle: 'fixed',
                            modalColor : '#000',
                            opacity: 0.8,
                            easing: 'easeInOutExpo', //uses jQuery easing plugin
                            speed: 400,
                            transition: 'slideDown',
                            onOpen: function() {
                                $('#concept-' + concept_id.toString() + '-expanded-popup-' + snippet_num.toString() + ' .expanded-popup-content').mCustomScrollbar({
                                    theme: 'custom-dark-thin',
                                    scrollButtons: {
                                        enable: false
                                    }
                                });
                            },
                            onClose: function() { 
                                $('#concept-' + concept_id.toString() + '-expanded-popup-' + snippet_num.toString()).remove(); 
                            }
                        });
                });
            //}
        });
        el.children('.target-concept-div-right').children('.jcarousel').jcarousel('reload');
    }
    
    // load carousel-activate-panels for rest of concept nodes
    $('.target-concept-div').each(function(i) {
        var el = $(this);
        if(i>0) {
            var activateCaPanel = "";
            activateCaPanel += "<div id='carousel-activate-panel-" + i.toString() + "' class='carousel-activate-panel'><div class='panel-content'>CLICK TO LOAD SNIPPETS</div></div>";
            el.children('.target-concept-div-right').append(activateCaPanel);
            $('#carousel-activate-panel-' + i.toString()).click(function() {
                $(this).remove();
                var loadingCaPanel = "";
                loadingCaPanel += "<div id='carousel-loading-panel-" + i.toString() + "' class='carousel-loading-panel'><div class='panel-content'>LOADING . . .</div></div>";
                el.children('.target-concept-div-right').append(loadingCaPanel);
                loadingCaPanel_el = $('#carousel-loading-panel-' + i.toString());
                initItems(el, loadingCaPanel_el);
            });
        } else {
            // load carousel for first concept node only
            var loadingCaPanel = "";
            loadingCaPanel += "<div id='carousel-loading-panel-" + i.toString() + "' class='carousel-loading-panel'><div class='panel-content'>LOADING . . .</div></div>";
            el.children('.target-concept-div-right').append(loadingCaPanel);
            loadingCaPanel_el = $('#carousel-loading-panel-' + i.toString());
            initItems(el, loadingCaPanel_el);
        }
    });
}

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// on document ready
$(document).ready(function() {

    //~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // search panel
    $(window).scroll(function() {
        var yPos = -($(window).scrollTop() / 10); 
        var coords = '0 '+ yPos + 'px';
        $('#main').css({ backgroundPosition: coords });
    }); // create parallax effect
    $('#searchbox button').click(function(e) {
        if($('#searchbox input').val().length > 2) {
            activateSearch();
        }
    }); // calls search function for button
    $('#searchbox input').keypress(function(e) {
        if(e.which == 13) {
            if($('#searchbox input').val().length > 2) {
                activateSearch();
                $(this).blur();
            }
        }
    }); // calls search function on enter key
    $('#searchbox input').focus(function(e) {
        $('#search_selection_content').html("");
        $('#search_selection').hide();
        expandSearchPanel();
    }); // expands search panel on re-focus

    //~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // options panel
    $('#options_button button').click(function(e) {
        $('#options_panel').slideToggle();
        $(this).blur();
    }); // opens options panel
    $('.options-selected').each(function() {
        var selected = $(this);
        selected.siblings('.dropdown-menu').children('li').click(function(e) {
            selected.html($(this).html());
            selected.parent().attr('code', $(this).attr('code'));
        });
    }); // populates accompanying info box and updates code attribute
    $('.dropdown-menu').on('click', function(e) {
        if($(this).hasClass('dropdown-menu-form')) {
            e.stopPropagation();
        }
    }); // functionality to make checkbox selections
    $('#options_update button').click(function(e) {
        // google analytics event tracking
        _gaq.push(['_trackEvent', 'update_button', 'click']);    
        $('#options_panel').hide();
        updateNodes($('#concept_nodes .source-concept').attr('concept_id'));
    }); // calls update function
    
    expandSearchPanel(); // expand search panel animation on start
    loadCatFilterGroup();
    loadRespacksGroup();
    
});

});