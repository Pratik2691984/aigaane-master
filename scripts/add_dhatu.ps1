param(
    [string]$Id,
    [string]$Upadesha,
    [string]$Root,
    [string]$Romanized,
    [string]$CanonicalForm,
    [string]$GanaId,
    [string]$ItStatus,
    [string]$Karmatva,
    [string]$DefaultPada,
    [string]$SemanticsSanskrit,
    [string]$SemanticsEnglish,
    [string]$LatKartariParasmaipada = "",
    [string]$LotKartariParasmaipada = "",
    [string]$LatKartariAtmanepada = "",
    [string]$LotKartariAtmanepada = "",
    [string]$LatBhavaKarmaniAtmanepada = "",
    [string]$SanantaBase = "",
    [string]$NijantaBase = "",
    [string]$YangantaBase = "",
    [string]$UpasargaList = ""
)

$csvPath = "raw/dhatupatha.csv"

$row = [PSCustomObject]@{
    id = $Id
    upadesha = $Upadesha
    root = $Root
    romanized = $Romanized
    canonicalForm = $CanonicalForm
    gana_id = $GanaId
    itStatus = $ItStatus
    karmatva = $Karmatva
    defaultPada = $DefaultPada
    semantics_sanskrit = $SemanticsSanskrit
    semantics_english = $SemanticsEnglish
    lat_kartari_parasmaipada = $LatKartariParasmaipada
    lot_kartari_parasmaipada = $LotKartariParasmaipada
    lat_kartari_atmanepada = $LatKartariAtmanepada
    lot_kartari_atmanepada = $LotKartariAtmanepada
    lat_bhavaKarmani_atmanepada = $LatBhavaKarmaniAtmanepada
    sananta_base = $SanantaBase
    nijanta_base = $NijantaBase
    yanganta_base = $YangantaBase
    upasarga_list = $UpasargaList
}

if (!(Test-Path $csvPath)) {
    $row | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
}
else {
    $row | Export-Csv -Path $csvPath -NoTypeInformation -Append -Encoding UTF8
}

Write-Host "Added dhatu: $Id $Root"