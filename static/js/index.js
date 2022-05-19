// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // sign up fields
        sign_up_email: "",
        sign_up_first_name: "",
        sign_up_last_name: "",
        sign_up_password: "",
        // log in fields
        log_in_email: "",
        log_in_password: "",
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };
    
    app.login = function() {
        if (app.vue.log_in_email != "" && app.vue.log_in_password != "") {
            let self = this;
            axios.post(login_url,
                {
                    email: app.vue.log_in_email,
                    password: app.vue.log_in_password,
                }).then(function (response) {
                    console.log('login attempt successful');
                    window.location = index_url;
                }).catch(function (error) {
                    console.log('an error occured');
                    console.log(error);
                });
        }
    };

    app.signup = function(props) {
        if (app.vue.sign_up_email != "" && app.vue.sign_up_first_name != ""
            && app.vue.sign_up_last_name != "" && app.vue.sign_up_password != "") {

            axios.post(sign_up_url,
                {
                    email: app.vue.sign_up_email,
                    first_name: app.vue.sign_up_first_name,
                    last_name: app.vue.sign_up_last_name,
                    password: app.vue.sign_up_password,
                }
            ).then(function (response) {
                console.log('sign up attempt successful');
                app.vue.log_in_email = app.vue.sign_up_email;
                app.vue.log_in_password = app.vue.sign_up_password;
                app.login();
            }).catch(function (error) {
                console.log('an error occured');
                console.log(error);
            });
        }
    };

    // This contains all the methods
    app.methods = {
        login: app.login,
        signup: app.signup,
    };

    // This creates the Vue instance
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    app.init = () => {
        // Put here any initialization code
    };

    // Call to the initializer
    app.init();
};

// Initialize the app object
init(app);