using System.Text.Encodings.Web;
using System.Text.Json;
using CoreServer;
using CoreServer.Middleware;

var builder = WebApplication.CreateBuilder(args);

string configPath = Path.Combine(AppContext.BaseDirectory, "..", "config.json");
if (!File.Exists(configPath))
    configPath = Path.Combine(AppContext.BaseDirectory, "config.json");

int port = 11450;
string dbPath = Path.Combine("data", "xiu_xian.db");
if (File.Exists(configPath))
{
    try
    {
        using var doc = JsonDocument.Parse(File.ReadAllText(configPath));
        if (doc.RootElement.TryGetProperty("db", out var db))
        {
            if (db.TryGetProperty("sqlite_path", out var p))
                dbPath = p.GetString() ?? dbPath;
        }
        if (doc.RootElement.TryGetProperty("core_server", out var cs))
        {
            if (cs.TryGetProperty("port", out var pp))
                port = pp.GetInt32();
        }
    }
    catch { }
}

builder.WebHost.ConfigureKestrel(opt =>
{
    opt.ListenLocalhost(port);
});

builder.Services.AddSingleton(new Database(dbPath));

builder.Services.AddControllers().AddJsonOptions(o =>
{
    o.JsonSerializerOptions.Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping;
});

CoreServer.Utils.Localization.GetStageDescriptions("EN");
CoreServer.Utils.Localization.GetStageDescriptions("CHS");
CoreServer.Utils.Localization.GetStageMax();

string apiSecret = Environment.GetEnvironmentVariable("API_SECRET") ?? string.Empty;

var app = builder.Build();

app.UseMiddleware<ApiKeyMiddleware>(apiSecret);


app.MapGet("/health", () => Results.Json(new
{
    status = "healthy",
    timestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds()
}));

app.MapControllers();

app.Run();
