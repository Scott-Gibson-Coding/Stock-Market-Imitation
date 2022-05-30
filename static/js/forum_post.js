// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        comment_list: [],
        current_user_name: "",
        current_user_email: "",
        current_comment: "",
        adding_comment: false,
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.complete = (a) => {
        // Add reaction for thumbs
        a.map((e) => {
            e.reaction = 0;
        });
        return a
    };

    app.start_comment = function(){
        // Open field
        app.vue.adding_comment = true;
    };

    app.cancel_comment = function(){
        // Clear input field and hide comment
        app.vue.adding_comment = false;
        app.vue.current_comment = "";
    };

    app.post_comment = function(){
        // Send the post to the server if not empty
        if (app.vue.current_comment != ""){
            let original_text = app.vue.current_comment;
            axios.post(post_comment_url, {'comment_text' : original_text}
            ).then(function(response){
                // Add to reactive list
                //console.log(response.data);
                let new_comment = Object.assign({}, response.data);
                delete new_comment.flash;
                new_comment.comment = original_text;
                // Add reactive variables to the new post
                app.complete([new_comment]);
                new_comment['likes'] = 0;
                new_comment['dislikes'] = 0;
                // Place at front of list and redo indices
                app.vue.comment_list.unshift(new_comment);
                app.enumerate(app.vue.comment_list);
                app.cancel_comment();
            });
        }
    };

    app.delete_comment = function(comment_idx){
        let comment = app.vue.comment_list.splice(comment_idx, 1)[0];
        app.enumerate(app.vue.comment_list);
        axios.get(delete_comment_url, {'params':{'comment_id':comment.id}});
    };

    app.react = function(comment_idx, react){
        let comment = app.vue.comment_list[comment_idx];
        // Change the reaction state
        if (react === 'up'){
            if (comment.reaction === 1){
                comment.reaction = 0;
                comment.likes--;
            } else{
                if (comment.reaction === -1){
                    comment.dislikes--;
                }
                comment.reaction = 1;
                comment.likes++;
            }
        } else if (react === 'down'){
            if (comment.reaction === -1){
                comment.reaction = 0;
                comment.dislikes--;
            } else{
                if (comment.reaction === 1){
                    comment.likes--;
                }
                comment.reaction = -1;
                comment.dislikes++;
            }
        }
        // Save the new reaction to the db
        axios.post(save_reaction_url, 
            {'comment_id' : comment.id, 'reaction' : comment.reaction}
        );
    };

    // This contains all the methods
    app.methods = {
        start_comment: app.start_comment,
        cancel_comment: app.cancel_comment,
        post_comment: app.post_comment,
        delete_comment: app.delete_comment,
        react: app.react,
    };

    // This creates the Vue instance
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    app.init = () => {
        // Get the comments for the current post
        // as well as the post details
        axios.get(get_comments_url).then(function(response){
            // Save the comments
            let comments = response.data.comments;
            app.enumerate(comments);
            app.complete(comments);
            app.vue.comment_list = comments;
            // Save current user name and email
            app.vue.current_user_name = response.data.current_user_name;
            app.vue.current_user_email = response.data.current_user_email;
            // Get reactions
            let reactions = response.data.reactions;
            // Pair with correct comment
            for (let react of reactions){
                let c = app.vue.comment_list.find(el=>el.id === react.comment_id);
                c.reaction = react.reaction;
            }
        });
    };

    // Call to the initializer
    app.init();
};

// Initialize the app object
init(app);