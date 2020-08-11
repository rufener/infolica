
/**
 * Handle exception
 */
export const handleException = function (error, component) {
    //Error code
    var code = error && error.response && error.response.status || 500;
    
    //No error but no content response
    if(error && error.status === 204){
        component.$root.$emit("ShowError", "Aucune donnée trouvée");   
    }
    //Not authorized
    else if(code === 403){
        component.$root.$emit("ShowError", "Veuillez vous connecter pour continuer"); 
        if(component.$router && component.$router.currentRoute && component.$router.currentRoute.name != 'Login')
            component.$router.push({name: "Login"});
    }
    //Custom error
    else if(error && error.msg){
        component.$root.$emit("ShowError", error.msg);   
    }
    //All other error codes
    else
    {
       component.$root.$emit("ShowError", "Une erreur est survenue");   
    }                  
};

