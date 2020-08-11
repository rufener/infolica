<style src="./login.css" scoped></style>
<template src="./login.html"></template>


<script>
import {handleException} from '@/services/exceptionsHandler';
import {setCurrentUserFunctions} from '@/services/helper';

export default {
  name: 'Login',
  props: {},
  data: () => {
    return {
      showProgess: false
    }
  },
  methods:{

        /**
         * Login
         */
        async doLogin () {
            this.showProgess = true;
            var formData = new FormData();
            formData.append("login", this.$refs.username.value);
            formData.append("password", this.$refs.userpass.value);

            this.$http.post(
              process.env.VUE_APP_API_URL + process.env.VUE_APP_LOGIN_ENDPOINT, 
              formData,
              {
                withCredentials: true,
                headers: {"Accept": "application/json"}
              }
            )
            .then(response =>{
              if(response && response.data){
                this.processLogin(response.data);
                this.$router.push({ name: "Affaires"});
              }
            })
            //Error 
            .catch(err => {
              this.showProgess = false;
              handleException(err, this);
            })
          },
          
          /**
           * Logout
           */
          async doLogout () {
            this.$http.get(
              process.env.VUE_APP_API_URL + process.env.VUE_APP_LOGOUT_ENDPOINT, 
              {
                withCredentials: true,
                headers: {"Accept": "application/json"}
              }
            )
            .then(() =>{
              localStorage.removeItem('infolica_user');
            })
            //Error 
            .catch(err => {
              handleException(err, this);
            })
          },


          /**
           * Process login
           */
          processLogin (data) {
            localStorage.setItem('infolica_user', JSON.stringify(data));
            setCurrentUserFunctions();
            this.$root.$emit('infolica_user_logged_in', data);
          },

          /**
           * Process logout
           */
          processLogout () {
            localStorage.setItem('infolica_user', null);
            this.$root.$emit('infolica_user_logged_out');

            if(this.$router && this.$router.currentRoute && this.$router.currentRoute.name != 'Login')
              this.$router.push({ name: "Login"});
          }
    },

    mounted: function(){
      //Logout
      this.$root.$on("infolica_user_logout", () =>{        
        this.doLogout();    
        this.processLogout();    
      });
    }
}
</script>

