## .NET Framework 
**ASP.NET Web API** 
1. From the .csproj file references: xx.Web.csproj
``` 
<Reference Include="System.Web.Http, Version=5.2.3.0" />
<Reference Include="System.Web.Http.Cors" />
<Reference Include="System.Web.Http.OData, Version=4.0.0.0" />
```

2. From the packages.config: packages.config
```
<package id="Microsoft.AspNet.Mvc" version="5.2.3" targetFramework="net45" />
<package id="Microsoft.AspNet.WebPages" version="3.2.3" targetFramework="net45" />
<package id="Microsoft.AspNet.WebApi" version="5.2.3" targetFramework="net45" />
<package id="Microsoft.AspNet.Cors" version="5.2.3" targetFramework="net45" />
```

3. Here are the general web controller method signatures and patterns commonly used in ASP.NET Web API and ASP.NET Core: xx.cs  
**In classic Web API, use [FromUri] instead of [FromQuery] (which is for ASP.NET Core).**

3.1 Basic HTTP Verb Attributes
```c#
public class ProductsController : ApiController
{
    [HttpGet]
    public IHttpActionResult Get()
    
    [HttpGet]
    public IHttpActionResult Get(int id)
    
    [HttpPost]
    public IHttpActionResult Post([FromBody] Product product)
    
    [HttpPut]
    public IHttpActionResult Put(int id, [FromBody] Product product)
    
    [HttpDelete]
    public IHttpActionResult Delete(int id)
    
    [HttpPatch]
    public IHttpActionResult Patch(int id, [FromBody] JsonPatchDocument<Product> patchDoc)
    
    [HttpHead]
    public IHttpActionResult Head()
    
    [HttpOptions]
    public IHttpActionResult Options()
}
```

3.2 Parameter Binding Attributes
Parameter Binding Attributes are special annotations in ASP.NET that tell the framework where to get the data for action method parameters from incoming HTTP requests.

The Problem They Solve  
When an HTTP request comes in, the framework needs to know:
```c#
Should this parameter come from the URL?
From the request body?
From query string?
From headers?
```  

Parameter binding attributes explicitly specify the source.  

Common Parameter Binding Attributes  
3.2.1. `[FromQuery]` - Query String Parameters
```c#
// GET /api/products?search=laptop&page=2&size=10
[HttpGet]
public IActionResult GetProducts(
    [FromQuery] string search,     // Gets "laptop" from ?search=laptop
    [FromQuery] int page,          // Gets 2 from &page=2  
    [FromQuery] int size = 20)     // Gets 10 from &size=10 (or default 20)
{
    // search = "laptop", page = 2, size = 10
}
```
3.2.2.  `[FromRoute]` - URL Path Parameters
```c#
// GET /api/products/123/reviews/456
[HttpGet("{productId}/reviews/{reviewId}")]
public IActionResult GetReview(
    [FromRoute] int productId,     // Gets 123 from URL path
    [FromRoute] int reviewId)      // Gets 456 from URL path
{
    // productId = 123, reviewId = 456
}
```
3.2.3. `[FromBody]` - Request Body (JSON/XML)
```c#
// POST /api/products
// Content-Type: application/json
// Body: {"name": "Laptop", "price": 999.99}
[HttpPost]
public IActionResult CreateProduct([FromBody] Product product)
{
    // product.Name = "Laptop", product.Price = 999.99
    // Entire object deserialized from JSON body
}
```
3.2.4. `[FromForm]` - Form Data
```c#
// POST /api/upload
// Content-Type: multipart/form-data
[HttpPost]
public IActionResult Upload(
    [FromForm] IFormFile file,        // File from form
    [FromForm] string description,    // Text field from form
    [FromForm] bool isPublic)         // Checkbox from form
{
    // Gets data from HTML form submission
}
```
3.2.5. `[FromHeader]` - HTTP Headers
```c#
[HttpGet]
public IActionResult GetData(
    [FromHeader] string authorization,           // From Authorization header
    [FromHeader(Name = "X-API-Key")] string apiKey,  // From custom header
    [FromHeader] string userAgent)               // From User-Agent header
{
    // authorization = "Bearer abc123..."
    // apiKey = "xyz789..."
}
```
3.2.6. `[FromServices]` - Dependency Injection
```c#
[HttpGet]
public IActionResult GetProducts(
    [FromServices] IProductService productService,  // Injected service
    [FromQuery] string category)                     // Query parameter
{
    var products = productService.GetByCategory(category);
    return Ok(products);
}
```
Real-World Example
```c#
[ApiController]
[Route("api/[controller]")]
public class OrdersController : ControllerBase
{
    // POST /api/orders/123/items?notify=true
    // Headers: Authorization: Bearer abc123, X-Correlation-ID: xyz
    // Body: {"productId": 456, "quantity": 2}
    [HttpPost("{orderId}/items")]
    public async Task<IActionResult> AddOrderItem(
        [FromRoute] int orderId,                    // 123 from URL
        [FromQuery] bool notify,                    // true from ?notify=true
        [FromBody] OrderItemRequest request,        // JSON from request body
        [FromHeader] string authorization,          // Bearer token
        [FromHeader(Name = "X-Correlation-ID")] string correlationId,
        [FromServices] IOrderService orderService)  // Injected service
    {
        // orderId = 123
        // notify = true  
        // request.ProductId = 456, request.Quantity = 2
        // authorization = "Bearer abc123"
        // correlationId = "xyz"
        
        var result = await orderService.AddItem(orderId, request);
        return Ok(result);
    }
}
```
Default Binding Behavior (Without Attributes)  
If you don't specify attributes, ASP.NET Core follows these rules:  
```c#
[HttpPost("{id}")]
public IActionResult Update(
    int id,                    // Inferred as [FromRoute] - comes from URL
    string search,             // Inferred as [FromQuery] - simple types from query
    Product product)           // Inferred as [FromBody] - complex types from body
{
    // Framework automatically figures out the sources
}
```
  
Complex Object Binding
```c#
public class SearchRequest
{
    public string Query { get; set; }
    public int Page { get; set; }
    public int PageSize { get; set; }
    public string[] Categories { get; set; }
}

// GET /api/search?query=laptop&page=1&pageSize=20&categories=electronics&categories=computers
[HttpGet]
public IActionResult Search([FromQuery] SearchRequest request)
{
    // Automatically binds all query parameters to object properties
    // request.Query = "laptop"
    // request.Page = 1
    // request.PageSize = 20  
    // request.Categories = ["electronics", "computers"]
}
```


```c#
public class ApiController : ControllerBase
{
    // Query string parameters
    [HttpGet]
    public IActionResult Get([FromQuery] string search, [FromQuery] int page = 1)
    
    // Route parameters
    [HttpGet("{id}")]
    public IActionResult GetById([FromRoute] int id)
    
    // Request body (JSON/XML)
    [HttpPost]
    public IActionResult Create([FromBody] CreateRequest request)
    
    // Form data
    [HttpPost]
    public IActionResult Upload([FromForm] IFormFile file, [FromForm] string description)
    
    // Headers
    [HttpGet]
    public IActionResult Get([FromHeader] string authorization, [FromHeader(Name = "X-Custom")] string custom)
    
    // Services (dependency injection)
    [HttpGet]
    public IActionResult Get([FromServices] IMyService service)
    
    // Multiple sources
    [HttpPost("{id}")]
    public IActionResult Update([FromRoute] int id, [FromBody] UpdateRequest request, [FromQuery] bool validate = true)
}
```

3.3 Route Templates
```c#
[Route("api/[controller]")]
public class ProductsController : ControllerBase
{
    // GET api/products
    [HttpGet]
    public IActionResult GetAll()
    
    // GET api/products/5
    [HttpGet("{id}")]
    public IActionResult Get(int id)
    
    // GET api/products/5/reviews
    [HttpGet("{id}/reviews")]
    public IActionResult GetReviews(int id)
    
    // GET api/products/search?q=laptop
    [HttpGet("search")]
    public IActionResult Search([FromQuery] string q)
    
    // POST api/products
    [HttpPost]
    public IActionResult Create([FromBody] Product product)
    
    // PUT api/products/5
    [HttpPut("{id}")]
    public IActionResult Update(int id, [FromBody] Product product)
    
    // DELETE api/products/5
    [HttpDelete("{id}")]
    public IActionResult Delete(int id)
}
```
3.4 Return Types
```c#
public class ApiController : ControllerBase
{
    // IActionResult (most flexible)
    [HttpGet]
    public IActionResult Get() => Ok(data);
    
    // ActionResult<T> (strongly typed)
    [HttpGet]
    public ActionResult<Product> Get() => product;
    
    // Direct type (auto-wrapped in 200 OK)
    [HttpGet]
    public Product Get() => product;
    
    // Task for async operations
    [HttpGet]
    public async Task<IActionResult> GetAsync()
    
    [HttpGet]
    public async Task<ActionResult<List<Product>>> GetAllAsync()
    
    // Specific status codes
    [HttpPost]
    public IActionResult Create([FromBody] Product product)
    {
        // Created (201)
        return CreatedAtAction(nameof(Get), new { id = product.Id }, product);
        
        // Bad Request (400)
        return BadRequest("Invalid data");
        
        // Not Found (404)
        return NotFound();
        
        // No Content (204)
        return NoContent();
        
        // Custom status
        return StatusCode(418, "I'm a teapot");
    }
}
```
3.5 Advanced Routing Patterns
```c#
[ApiController]
[Route("api/v{version:apiVersion}/[controller]")]
public class ProductsController : ControllerBase
{
    // Constraint routing
    [HttpGet("{id:int:min(1)}")]
    public IActionResult Get(int id)
    
    // Optional parameters
    [HttpGet("{category?}")]
    public IActionResult GetByCategory(string category = "all")
    
    // Multiple routes
    [HttpGet]
    [HttpGet("all")]
    [HttpGet("list")]
    public IActionResult GetAll()
    
    // Route names for link generation
    [HttpGet("{id}", Name = "GetProduct")]
    public IActionResult Get(int id)
    
    // Complex route templates
    [HttpGet("{category}/{subcategory:alpha}/{id:int}")]
    public IActionResult GetSpecific(string category, string subcategory, int id)
}
```

3.6 Authentication & Authorization
```c#
[Authorize]
public class SecureController : ControllerBase
{
    [HttpGet]
    [AllowAnonymous]
    public IActionResult Public()
    
    [HttpGet]
    [Authorize(Roles = "Admin")]
    public IActionResult AdminOnly()
    
    [HttpGet]
    [Authorize(Policy = "MinimumAge")]
    public IActionResult PolicyBased()
    
    [HttpPost]
    [Authorize(AuthenticationSchemes = "Bearer")]
    public IActionResult JwtProtected()
}
```  

3.7 Content Negotiation  
The client tells the server what formats it prefers using HTTP headers, and the server responds with the most appropriate format.

Client Request Headers:
Accept - What response formats the client can handle
Accept-Language - Preferred languages
Accept-Encoding - Compression formats (gzip, deflate)
Content-Type - Format of data being sent to server

Server Response Headers:
Content-Type - Format of the response data
Content-Language - Language of the response
Content-Encoding - Compression used  
```c#
public class ApiController : ControllerBase
{
    [HttpGet]
    [Produces("application/json")]
    public IActionResult GetJson()
    
    [HttpGet]
    [Produces("application/xml", "application/json")]
    public IActionResult GetMultiFormat()
    
    [HttpPost]
    [Consumes("application/json")]
    public IActionResult PostJson([FromBody] object data)
    
    [HttpPost]
    [Consumes("multipart/form-data")]
    public IActionResult PostForm([FromForm] IFormFile file)
}
```




```c#
[HttpGet]
public IActionResult GetDevices([FromQuery] RequestParameters parameters)
{
    // This indicates 'parameters' comes from HTTP query string
}
```

## The main differences between IActionResult and ActionResult in ASP.NET Core relate to interface vs class, flexibility, and type safety.  

|Feature | `IActionResult` | `ActionResult` | `ActionResult<T>`
|:--- | :--- | :--- | :---|
|Type | Interface | Abstract Class | Generic Class
|Flexibility | Highest | High | Medium
|Type Safety | None | None | High
|Best For | MVC Views, Mixed APIs | General use | API endpoints
|Swagger Docs | Manual | Manual | Automatic
|IntelliSense | Generic | Generic | Strongly typed

**Recommendation:**  
Use ActionResult<T> for API controllers with consistent return types  
Use IActionResult for MVC controllers or when you need maximum flexibility  
ActionResult (non-generic) is rarely used directly - stick with the interface or generic version  

**Real-World Usage Patterns**  
**1. API Controllers (Recommended: ActionResult<T>)**  
```c#
[ApiController]
[Route("api/[controller]")]
public class ProductsController : ControllerBase
{
    // ✅ Best for APIs - type-safe and clear
    [HttpGet("{id}")]
    public ActionResult<Product> Get(int id)
    {
        var product = productService.GetById(id);
        return product ?? NotFound();
    }
    
    [HttpGet]
    public ActionResult<List<Product>> GetAll()
    {
        return productService.GetAll();
    }
    
    [HttpPost]
    public ActionResult<Product> Create(Product product)
    {
        var created = productService.Create(product);
        return CreatedAtAction(nameof(Get), new { id = created.Id }, created);
    }
}
```

**2. MVC Controllers (Use IActionResult)**  
```c#
public class HomeController : Controller
{
    // ✅ Good for MVC - returns views, redirects, etc.
    public IActionResult Index()
    {
        return View();
    }
    
    public IActionResult Privacy()
    {
        return View();
    }
    
    [HttpPost]
    public IActionResult Contact(ContactModel model)
    {
        if (!ModelState.IsValid)
            return View(model);
            
        // Process form
        return RedirectToAction("Success");
    }
}
```

## .NET Core

