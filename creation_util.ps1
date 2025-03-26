# importer les modules nÃ©cessaires

Import-Module ActiveDirectory

# fonction de crÃ©ation de l'utilisateur

Function Create_User {
    param (
        [string]$Nom,
        [string]$Prenom,
        [string]$Mail,
        [string]$Password,
        [string]$CompagnyName
    )
    # convertir le mdp en chaine de caractere sÃ©curisÃ©
    $Password_secured = ConvertTo-SecureString $Password -AsPlainText -Force
    #Â on clear ensuite la variable pour des raisons de sÃ©curitÃ©
    Clear-Variable -Name "Password"
 
    $Fullname = "$Prenom $Nom"
    $DisplayName_build = "$Fullname $CompagnyName"
    $Username = ($Mail).split("@")[0]
    $DomaineName = ($Mail).split("@")[1]
    $SamAccountName = $Username -replace '[^a-zA-Z0-9]', ''  # Supprime tout caractère non alphanumérique
    $UserPrincipalName = "$SamAccountName@INFOWA.PROJET.LOCAL"
    
    $NewUserParam = @{
        Name = $Fullname
        DisplayName = $DisplayName_build
        GivenName = $Prenom
        Surname = $Nom
        SamAccountName = $SamAccountName
        UserPrincipalName = $UserPrincipalName
        EmailAddress = $Mail
        Path = "OU=Utilisateurs,OU=INFOWA,DC=infowa,DC=projet,DC=local"
        AccountPassword = $Password_secured
        ChangePasswordAtLogon = $false
        Enabled = $true
        OtherAttributes = @{"proxyaddresses"="SMTP:$Mail"}
    }

    # Création de l'utilisateur
    try {
        New-ADUser @NewUserParam
        Write-Host "Utilisateur créé avec succès : $Fullname"
    }
    catch {
        Write-Error "Erreur lors de la création de l'utilisateur : $_"
    }
}   

# fonction d'export de l'utilisateur dans la base de donnÃ©e

Function Export_BDD {
    param (
        [string]$Utilisateur,
        [int]$ID_Prise,
        [string]$Hostname
    )
    
    # On utilise MysqlSH pour ne pas avoir a installer le serveur Mysql mais que le client
    $result_requete = mysqlsh --sql -h "" -P "" --password= -u "" -D ProjetE6_New -e "INSERT INTO Utilisateur_PC_Prise (UPN_Utilisateur, hostname, id_prise) VALUES('$Utilisateur', '$Hostename', '$ID_Prise');"
    Write-Output $result_request
}

#Â partie utilisateur

$Nom = Read-Host "Entrez le nom de l'utilisateur "
$Prenom = Read-Host "Entrez le prenom de l'utilisateur "
$Mail = Read-Host "Entrez le mail de l'utilisateur "
$Compagny = Read-Host "Entrez le nom de la sociÃ©tÃ© "
$Password = Read-Host "Entrez le mot de passe de l'utilisateur " -MaskInput
$Prise = Read-Host "Entrez l'id de la prise "
$Hostename = Read-Host "Entrez le hostname du PC "


Create_User -Nom $Nom -Prenom $Prenom -Mail $Mail -Password $Password -CompagnyName $Compagny
Export_BDD -Utilisateur $Mail -ID_Prise $Prise -Hostename $Hostename