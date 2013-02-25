$(document).ready(function() {

    $('#fieldSelect').clone(true).appendTo($("#include"));
    $('#fieldSelect').clone(true).appendTo($("#exclude"));


   $(".addTerm").live('click', function() {
            $('#fieldSelect').clone(true).append(
                $("#removeParent").clone(true)
            ).appendTo($(this).parent().parent().find(".terms"));
    });


    $(".removeParent").live('click', function() {
        $(this).parent().remove();
        generateQueryString();
    });


    $(".attrSelect").live('change', function() {
        // Build a dictionary for the autocomplete
        var autocomplete = $(this).parent().find('input').typeahead();

        autocomplete.data('typeahead').select = function () {
            var val = this.$menu.find('.active').attr('data-value');
            this.$element.val(val);
            generateQueryString();
            return this.hide();
        };

        // GLOBAL_DATA_SOURCE is defined in the template 
        autocomplete.data('typeahead').source = GLOBAL_DATA_SOURCE[
            $(this).find(":selected").val()];
    });


    $(".queryValue").on('keyup', generateQueryString);


    function generateQueryString() {

        function getCludeQuery(clude) {
            var cludeQuery = {};
            $(clude).find(".selection").each(function() {
                
                var attr = $(this).live('find',
                    '.attrSelect').find(":selected").val();

                var value = $(this).find('input').attr('value');
                if (typeof cludeQuery[attr] === 'undefined') {
                    cludeQuery[attr] = [];
                }
                cludeQuery[attr][cludeQuery[attr].length] = value;
            });
            return cludeQuery;
        }

        var includes = getCludeQuery("#include");
        var excludes = getCludeQuery("#exclude");

        function joinTerms(terms, innerJoinFunc, outerJoinFunc) {
            var count = 0;
            var queryString = [];
            $.each(terms, function(attr_name, outer_value) {
                var inner_queries = [];
                var inner_index = 0;
                $.each(outer_value, function(index, value) {
                    if (value) {
                     inner_queries[inner_index] = attr_name + ':' + '"' + value + '"';
                        inner_index++;
                    }
                });
                if (inner_queries.length > 0) {
                    queryString[count] = innerJoinFunc(inner_queries);
                    count++;
                }
            });
            queryString = outerJoinFunc(queryString);
            return queryString;
        }

        var includeString = joinTerms(includes, function(parts) {
            return "(" + parts.join(" OR ") + ")";
        }, function(parts) {
            return parts.join(" AND ");
        });

        var excludeString = joinTerms(excludes, function(parts) {
            return parts.join(" OR ");
        }, function(parts) {
            return parts.join(" OR ");
        });

        var current_query = '';
        
        if (includeString && excludeString) {
            current_query = [includeString, "(" + excludeString + ")"].join(" AND NOT ");
        }
        else if (includeString) {
            current_query = includeString;
        }
        else if (excludeString) {
            current_query = "NOT ("+excludeString+")";
        }

        $("#generated_query").attr('value', current_query);

    }
});
