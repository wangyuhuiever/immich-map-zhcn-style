Add-Type -AssemblyName System.Web.Extensions

$serializer = New-Object System.Web.Script.Serialization.JavaScriptSerializer
$serializer.MaxJsonLength = [int]::MaxValue

$wc = New-Object System.Net.WebClient
$lightRaw = $wc.DownloadString("https://tiles.immich.cloud/v1/style/light.json")
$darkRaw = $wc.DownloadString("https://tiles.immich.cloud/v1/style/dark.json")

function TransformStyle($styleJson, $mode, $theme) {
    $style = $serializer.DeserializeObject($styleJson)
    $style["id"] = "immich-map-" + $theme + "-" + $mode
    $style["name"] = "Immich Map (" + $theme + " - " + $mode + ")"
    
    $layers = $style["layers"]
    foreach ($layer in $layers) {
        if ($layer["type"] -eq "symbol") {
            $id = $layer["id"]
            $layout = $layer["layout"]
            if ($layout -and $layout.ContainsKey("text-field")) {
                if ($id -ne "address_label" -and $id -ne "roads_oneway") {
                    if ($mode -eq "zh-cn") {
                        if ($id -eq "places_region") {
                            $lowZoomExpr = @("coalesce", @("get", "name:zh-Hans"), @("get", "name:zh"), @("get", "name:zh-Hant"), @("get", "name"), @("get", "ref"))
                            $highZoomExpr = @("coalesce", @("get", "name:zh-Hans"), @("get", "name:zh"), @("get", "name:zh-Hant"), @("get", "name"), @("get", "name:en"))
                            $layout["text-field"] = @("step", @("zoom"), $lowZoomExpr, 6, $highZoomExpr)
                        } else {
                            $layout["text-field"] = @("coalesce", @("get", "name:zh-Hans"), @("get", "name:zh"), @("get", "name:zh-Hant"), @("get", "name"), @("get", "name:en"))
                        }
                    } else {
                        # bilingual
                        $allZh = @("has", "name:zh-Hans")
                        $allEn = @("has", "name:en")
                        $notEq = @("!=", @("get", "name:zh-Hans"), @("get", "name:en"))
                        $cond = @("all", $allZh, $allEn, $notEq)
                        $concatExpr = @("concat", @("get", "name:zh-Hans"), "`n", @("get", "name:en"))
                        $coalesceExpr = @("coalesce", @("get", "name:zh-Hans"), @("get", "name:zh"), @("get", "name:zh-Hant"), @("get", "name"), @("get", "name:en"))
                        
                        if ($id -eq "places_region") {
                            $lowZoomExpr = @("coalesce", @("get", "name:zh-Hans"), @("get", "name:zh"), @("get", "name"), @("get", "ref"))
                            $bilingualHighZoom = @("case", $cond, $concatExpr, $coalesceExpr)
                            $layout["text-field"] = @("step", @("zoom"), $lowZoomExpr, 6, $bilingualHighZoom)
                        } elseif ($id -eq "water_waterway_label" -or $id -eq "roads_labels_minor") {
                            $layout["text-field"] = $coalesceExpr
                        } else {
                            $layout["text-field"] = @("case", $cond, $concatExpr, $coalesceExpr)
                        }
                    }
                    
                    if ($id -eq "places_country") {
                        if ($layout.ContainsKey("text-transform")) {
                            [void]$layout.Remove("text-transform")
                        }
                    }
                }
            }
        }
    }
    return $serializer.Serialize($style)
}

$lightZh = TransformStyle $lightRaw "zh-cn" "light"
$darkZh = TransformStyle $darkRaw "zh-cn" "dark"
$lightBi = TransformStyle $lightRaw "bilingual" "light"
$darkBi = TransformStyle $darkRaw "bilingual" "dark"

$currentDir = $PSScriptRoot
[IO.File]::WriteAllText((Join-Path $currentDir "style-light.json"), $lightZh, [System.Text.Encoding]::UTF8)
[IO.File]::WriteAllText((Join-Path $currentDir "style-dark.json"), $darkZh, [System.Text.Encoding]::UTF8)
[IO.File]::WriteAllText((Join-Path $currentDir "style-light-bilingual.json"), $lightBi, [System.Text.Encoding]::UTF8)
[IO.File]::WriteAllText((Join-Path $currentDir "style-dark-bilingual.json"), $darkBi, [System.Text.Encoding]::UTF8)

Write-Host "All 4 map styles generated successfully in $currentDir"
