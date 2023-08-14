
/**
 * Handle exception
 */
export const handleException = function (error, component) {
    //Error code
    let code = error && error.response && error.response.status || 500;
    
    //No error but no content response
    if(error && error.status === 204){
        component.$root.$emit("ShowError", "Aucune donnée trouvée");   
    }
    //Not authorized
    else if(code === 403){
       component.$root.$emit("ShowError", "Veuillez vous connecter pour continuer"); 
    }
    //Custom error
    else if(error && error.msg){
        component.$root.$emit("ShowError", error.msg);   
    }
    //Back-end errors: show entire message
    else if (error && error.response && error.response.data && error.response.data.message)
    {
        component.$root.$emit("ShowError", "Une erreur est survenue, contacter l'administrateur. " + error.response.data.message);   
    }
    //Custom error
    else if(error){
        component.$root.$emit("ShowError", error);   
    }
    //All other error codes
    else
    {
       component.$root.$emit("ShowError", "Une erreur est survenue, contacter l'administrateur.");   
    }
};
