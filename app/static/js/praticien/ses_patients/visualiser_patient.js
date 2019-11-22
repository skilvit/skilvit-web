$("ajouter_fiche_seance").on("click", function ()
    {
        // TODO ajouter titre, date et texte
        console.log("ajouter_fiche_seance");
    }
);
$("ajouter_commentaire").on("click", function()
    {
        // TODO ajouter titre, date et texte
        console.log("ajouter_commentaire");
    }
);
// AJouter des tooltips sur les entrées qui ont un commentaires avec un petit icône qui montre qu'il y a
// un commentaire. Comme ça on peut lire le commentaire et pourquoi pas le modifier/supprimer en cliquant
// dessus.
// Faire usage de l'ajax pour ça.




function makeBlockAnamnese()
{
    var blockAnamnese = $.createElement("div");
        blockAnamnese.attr("class", "anamnese");
        blockAnamnese.attr("id", 'anamnese-'+$(this).attr("id"));

        var cancelButton = $.createElement("button");
        cancelButton.attr("class", "btn");
        cancelButton.attr("id", 'annuler-anamnese-'+$(this).attr("id"));

        var validateButton = $.createElement("button");
        validateButton.attr("class", "btn");

        var buttonLine = $.createElement("p");
        buttonLine.append(validateButton).append(cancelButton);

        blockAnamnese.append($.createElement("textarea"));
        blockAnamnese.append(buttonLine);

        blockAnamnese.css({
            position: 'relative',
            width: $(this).width(),
            top: $(this)
        })
        // set the textarea's value to be the saved content, or a default if there is no saved content
        .val(button.data('textContent') || 'This is my comment field\'s text')
        // set up a keypress handler on the textarea
        .keypress(function(e) {
            if (e.which === 13) { // if it's the enter button
                e.preventDefault(); // ignore the line break
                button.data('textContent', this.value); // save the content to the button
                $(this).remove(); // remove the textarea
            }
        })
        .insertAfter($(this)); // add the textarea to the document
}

// $(".commentaire").click(function(){
//    var texte_commentaire =  $(this).text();
//    var modification_commentaire = '<div>><textarea>' + texte_commentaire + '</textarea>'+
//        '<p><button class="btn annuler-modification-commentaire" id="annuler-modification-'+$(this).attr("id")+'">Annuler</button> ' +
//        '<button class="btn valider-modification-commentaire" id="valider-modification-'+$(this).attr("id")+'" name='+$(this).attr("name")+'>Valider</button></p></div>';
//
// });


$(".annotable").hover(function () {
    $(this).css("background-color", "#c0c0c0");
}, function(){
    $(this).css("background-color", "#ffffff")
}).click(function()
{
    console.log("oui");
    if($("#anamnese-"+$(this).attr("id")).length === 0)
    {
        console.log($("#anamnese-annotable-0").length);
        console.log("nombre : "+$("#anamnese-"+$(this).attr("id")).length);
        console.log("id : "+$(this).attr("id"));
        console.log("name : "+$(this).attr("name"));

        var anamneseText = '<div class="anamnese" id="anamnese-'+$(this).attr("id")+'"><textarea/>' +
            '<p><button class="btn annuler-anamnese-commentaire" id="annuler-anamnese-'+$(this).attr("id")+'">Annuler</button> ' +
            '<button class="btn valider-anamnese-commentaire" id="valider-anamnese-'+$(this).attr("id")+'" name='+$(this).attr("name")+'>Valider</button></p></div>';

        var button = $(this),
        commentField = $(anamneseText); // create a textarea element

        commentField.css({
            position: 'relative',
            width: $(this).width(),
            top: $(this)
        })
        // set the textarea's value to be the saved content, or a default if there is no saved content
        .val(button.data('textContent') || 'This is my comment field\'s text')
        // set up a keypress handler on the textarea
        .keypress(function(e) {
            if (e.which === 13) { // if it's the enter button
                e.preventDefault(); // ignore the line break
                button.data('textContent', this.value); // save the content to the button
                $(this).remove(); // remove the textarea
            }
        })
        .insertAfter($(this)); // add the textarea to the document

        onClickAnamneseCommentaireAnnuler($(this).attr("id"));
        onClickAnamneseCommentaireValider($(this).attr("id"));
    }
});


function addComment(text, insert_after_id, new_id)
{
    // var anamneseText = '<div class="anamnese commentaire" id="anamnese-'+$(this).attr("id")+'"><p>'+text+'</p></div>';
    var text_html = '<div class="commentaire" id="'+new_id+'"><p>'+text+
                                '<button class="close-remove-comment" aria-label="Close">' +
                                '<span aria-hidden="true">&times;</span>' +
                                '</button></p></div>';
    $(text_html).insertAfter($("#"+insert_after_id));

}