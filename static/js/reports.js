$(function(){
  $.ajax(
    {
      url: "/genomes/get-reports/",
      dataType: "json"
    }
  ).done(function( data ) {
    var obj = $.parseJSON(data);
    for (var idx in obj){
      console.log(obj[idx]['fields']['name']);
    }
  });
})
