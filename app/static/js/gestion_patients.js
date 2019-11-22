 var id_praticien= "probleme";

$(document).ready(function ()
{
    $("button.acceptation_patient").bind("click", function()
    {
        var button = $(this);
        var added_patient = $(this).attr("id");
        console.log(added_patient);
        $.ajax({
           url : "/tcc/ajax/praticien/ajouter_patient",
            data : {"email": $(this).attr("id")},
            type : "POST",
            success : function(data, statut)
            {
                if(data["ajoute"])
                {
                    $("ul#mes_patients").append("<li>"+data['prenom']+" "+ data['nom']+"</li>");

                    button.closest('li').remove();

                }
            }

        });
    });
});