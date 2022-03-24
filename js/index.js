// 功能：aws cloudfront 根域名跳转到www域名 根据seo,language路由
function handler(event) {
    var request = event.request;
    var uri = request.uri;
    var host = request.headers.host.value;
    var newurl = `https://www.${host}`; // Change the redirect URL to your choice
    var splitLength = request.headers.host.value.split('.').length;
    var user_agent = request.headers["user-agent"].value.toLowerCase();
    var seo_list = ['googlebot','bingbot','twitterbot','linkedinbot','mediapartners-google','naverbot','yeti']; // Seo header list 
    var lng_list = ['en-us','ko-kr','ja-jp','es-es','vi-vn'];

    // Redict Top-level domain to www domain
    if (splitLength  == 2){
        var response = {
            statusCode: 301,
            statusDescription: 'Moved Permanently',
            headers:
                { "location": { "value": newurl } }
            }
        return response;         
    }

    // Language routing,The default is index.html
    var isBoot = seo_list.some((c)=>user_agent.includes(c));
    if (!uri.includes('.') && !isBoot) {
        var res = lng_list.some((item)=>{
            if(uri.startsWith(`/${item}`)){
                request.uri = `/index.${item}.html`
                return true;
            }
            return false;
        });
            if(!res){
                request.uri = '/index.html';
            }
            return request;
    }

    // Seo routing
    else if (isBoot) {
        request.uri = uri;
        return request;
    }

    return request;
}
