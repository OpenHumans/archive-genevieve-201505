var getData = function(){
  $.ajax(
    {
      url: "/genomes/report/1/json",
      dataType: "json"
    }
  ).done(function( data ) {
    var obj = $.parseJSON(data);
    console.log(obj['fields']);
    for (var idx in obj['genomeanalysisvariants_dataset']){
      $('#genome-variants-table')
      .append($('<tr class="genome-variant"'+obj['genomeanalysisvariants_dataset'][idx]+'">')
      .append($('<td class="variant-chrom">'+obj['genomeanalysisvariants_dataset'][idx]['variant_data']['chrom']+'</td>'))
      .append($('<td class="variant-pos">'+obj['genomeanalysisvariants_dataset'][idx]['variant_data']['pos']+'</td>'))
      .append($('<td class="variant-ref">'+obj['genomeanalysisvariants_dataset'][idx]['variant_data']['ref_allele']+'</td>'))
      .append($('<td class="variant-alt">'+obj['genomeanalysisvariants_dataset'][idx]['variant_data']['alt_allele']+'</td>'))
      .append($('<td class="variant-freq">'+obj['genomeanalysisvariants_dataset'][idx]['variant_data']['freq']+'</td>'))
      .append($('<td class="genome-zyg">'+obj['genomeanalysisvariants_dataset'][idx]['zyg']+'</td>'))
      )
      for (var idx_2 in obj['genomeanalysisvariants_dataset'][idx]['variant_data']['clinvarrecords_dataset']){

        conditionURL = '<a href="http://www.ncbi.nlm.nih.gov/clinvar/'+obj['genomeanalysisvariants_dataset'][idx]['variant_data']['clinvarrecords_dataset'][idx_2]['accnum']+'">'+obj['genomeanalysisvariants_dataset'][idx]['variant_data']['clinvarrecords_dataset'][idx_2]['condition']+'</a>';
        commentaryURL = '<a href="/file_process/commentary/'+obj['genomeanalysisvariants_dataset'][idx]['variant_data']['clinvarrecords_dataset'][idx_2]+'"> View Variant Report</a>';

        $('#genome-variants-table')
        .append($('<tr class="genome-variant"'+obj['genomeanalysisvariants_dataset'][idx]['variant_data']['clinvarrecords_dataset'][idx_2]+'">')
        .append($('<td class="clinvar-clnsig">'+obj['genomeanalysisvariants_dataset'][idx]['variant_data']['clinvarrecords_dataset'][idx_2]['clnsig']+'</td>'))
        .append($('<td class="clinvar-condition">'+conditionURL+'</td>'))
        .append($('<td class="clinvar-accnum">'+commentaryURL+'</td>'))
        )
      }
      }
    }
  );
}

$(function(){
  getData();
});
