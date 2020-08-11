
import axios from 'axios';

/**
 * Check if the user is logged in
 */
export const checkLogged = function () {
    var session_user = JSON.parse(localStorage.getItem('infolica_user')) || null;
    
    //Set current user functions
    if(session_user)
        setCurrentUserFunctions();
    
    return session_user !== null;
};


/**
 * Check permission
 */
export const checkPermission = function (fonction) {
    var session_user = JSON.parse(localStorage.getItem('infolica_user')) || null;

    if(session_user && session_user.fonctions && session_user.fonctions.indexOf(fonction) > -1){
        return true;
    }

    return false;
};


/**
 * Get current user role id
 */
export const getCurrentUserRoleId = function () {
    var session_user = JSON.parse(localStorage.getItem('infolica_user')) || null;
    return (session_user && session_user.role_id) ? session_user.role_id : null;
};

/*
 * Set current user functions
 */
export const setCurrentUserFunctions = async function () {    
    axios.get(process.env.VUE_APP_API_URL + process.env.VUE_APP_CURRENT_USERS_FUNCTIONS_ENDPOINT,
        {
            withCredentials: true,
            headers: {"Accept": "application/json"}
        })
        .then(response =>{
            if(response && response.data){
                var session_user = JSON.parse(localStorage.getItem('infolica_user')) || null;
    
                if(session_user){
                    session_user.fonctions = response.data.fonctions;
                    session_user.role_id = response.data.role_id;
                    localStorage.setItem('infolica_user', JSON.stringify(session_user));
                }
            }
            })
        .catch(() => {
            //To do message
        });
};

/*
 * Get Cadastres
 */
export const getCadastres = async function () {
    return new Promise((resolve, reject) => {
        axios.get(process.env.VUE_APP_API_URL + process.env.VUE_APP_CADASTRES_ENDPOINT,
            {
              withCredentials: true,
              headers: {"Accept": "application/json"}
            })
            .then(response => resolve(response))
            .catch(() => reject);
    });
};

/*
 * Get Types Numeros
 */
export const getTypesNumeros = async function () {
    return new Promise((resolve, reject) => {
        axios.get(process.env.VUE_APP_API_URL + process.env.VUE_APP_TYPES_NUMEROS_ENDPOINT,
            {
              withCredentials: true,
              headers: {"Accept": "application/json"}
            })
            .then(response => resolve(response))
            .catch(() => reject);
    });
};

/*
 * Get Types Affaires
 */
export const getTypesAffaires = async function () {
    return new Promise((resolve, reject) => {
        axios.get(process.env.VUE_APP_API_URL + process.env.VUE_APP_TYPES_AFFAIRES_ENDPOINT,
            {
              withCredentials: true,
              headers: {"Accept": "application/json"}
            })
            .then(response => resolve(response))
            .catch(() => reject);
    });
};

/*
 * Get Etats Numeros
 */
export const getEtatsNumeros = async function () {
    return new Promise((resolve, reject) => {
        axios.get(process.env.VUE_APP_API_URL + process.env.VUE_APP_ETATS_NUMEROS_ENDPOINT,
            {
              withCredentials: true,
              headers: {"Accept": "application/json"}
            })
            .then(response => resolve(response))
            .catch(() => reject);
    });
};

/*
 * Get clients
 */
export const getClients = async function () {
    return new Promise((resolve, reject) => {
        axios.get(process.env.VUE_APP_API_URL + process.env.VUE_APP_CLIENTS_ENDPOINT,
            {
              withCredentials: true,
              headers: {"Accept": "application/json"}
            })
            .then(response => {
                response.data = setClientsAdresse_(response.data);
                resolve(response);
            })
            .catch(() => reject);
    });
};

export const setClientsAdresse_ = function(clients, sep=", ") {
    let isArray = true;
    if (!Array.isArray(clients)) {
        isArray = false;
        clients = [clients];        
    }
    
    clients.forEach(x => {
        x.adresse_ = [
            x.entreprise,
            [x.titre, x.prenom, x.nom].filter(Boolean).join(" "),
            x.co,
            x.adresse,
            x.case_postale !== null? "Case postale " + x.case_postale: null,
            [x.npa, x.localite].filter(Boolean).join(" ")
        ].filter(Boolean).join(sep);
    });

    if (!isArray) {
        clients = clients.pop();
    }

    return clients;
}

/**
 * Get date of the day in good format for BD
 */
export const getCurrentDate = function () {
    var today = new Date();
    var date =
        ("0" + today.getDate()).slice(-2) + "." + ("0" + (today.getMonth() + 1)).slice(-2) + "." + today.getFullYear();
    return date;
};

/**
 * Prépare la liste pour le md-complete
 */
export const stringifyAutocomplete = function(liste, nom="nom") {
    return liste.map(x => ({
        id: x.id,
        nom: String(x[nom]),
        toString: () => String(x[nom]).toString(),
        toLowerCase: () => String(x[nom]).toLowerCase()
    }));
};

/**
 * Générer les documents à partir des modèles
 */
export const getDocument = async function(formData) {
    return new Promise((resolve, reject) => {
        axios.post(process.env.VUE_APP_API_URL + process.env.VUE_APP_COURRIER_TEMPLATE_ENDPOINT,
            formData,
            {
                withCredentials: true,
                headers: { Accept: "application/html" }
            }
        ).then(response => {
            if (response && response.data) {
                const filename = response.data.filename;

                downloadGeneratedDocument(filename)
                .then(response => {
                    deleteGeneratedDocument(response)
                    .then(() => resolve(filename))
                    .catch(err => reject(err));
                })
            }
        })
        .catch(err => reject(err));
    });
};

/**
 * Download GeneratedDocument
 */
const downloadGeneratedDocument = async function(filename) {
    return new Promise(resolve => {
        let url =
        process.env.VUE_APP_API_URL +
        process.env.VUE_APP_COURRIER_TEMPLATE_ENDPOINT +
        "?filename=" +
        filename;
        window.open(url, "_blank");
        resolve(filename)
    });
};

/**
 * Delete generated document
 */
const deleteGeneratedDocument = async function(filename) {
    return new Promise((resolve, reject) => {
        new Promise(r => setTimeout(r, 200)).then(() => {

            axios.delete(process.env.VUE_APP_API_URL + process.env.VUE_APP_COURRIER_TEMPLATE_ENDPOINT +
                "?filename=" + filename,
                {
                    withCredentials: true,
                    headers: { Accept: "application/html" }
                }
            )
            .then(response => resolve(response))
            .catch(err => reject(err));
        });
    });    
};

/**
 * Search in list after n letters
 */
export const filterList = function(list, searchTerm, nLetters=0) {
    let result = [];

    if (typeof searchTerm !== "string") {
        return [];
    }

    if (searchTerm !== null) {
        let searchTerm_ = searchTerm.split(" ");

        let idx = searchTerm_.indexOf("");
        if (idx > -1) {
            searchTerm_.splice(idx, 1);
        }

        if (searchTerm.length >= nLetters) {
            result = list.filter(x => {
                return !searchTerm_.some(y => {
                    return !x.nom.toLowerCase().includes(y.toLowerCase());
                });
            });
        }
    }
    return result.slice(0,20);
};