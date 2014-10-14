function parseTime(time){
    var d=new Date();
    d.setTime(time*1000);
    return d;

}

function createCSV(){
    $(".token-table").each(function(){
        if ($(this).find(".temp-access-key").text()!=""){
            csvContent = "data:text/csv;charset=utf-8,";
            csvContent+="access key, secret key, session token \n";
            csvContent+=$(this).find(".temp-access-key").text()+","+
            $(this).find(".temp-secret-key").text()+","+
            $(this).find(".session-token").text()+"\n";
            encodedUri = encodeURI(csvContent);
            $(".download").attr("href",encodedUri);
        }
    });
}
$(document).ready(function(){
    $(".valid-until").each(function(){
        $(this).text(parseTime($(this).text()).toString());
    });
    createCSV();
})
