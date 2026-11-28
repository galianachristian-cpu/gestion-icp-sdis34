# Carte du code

_Générée par `node outils/carte.cjs`, ne pas modifier à la main. Numéros de ligne : début de chaque section._

# index.html : 94 sections, 700 fonctions

## EFFETS VISUELS · ligne 53

## DEUXIÈME VAGUE · ligne 106

## BANDEAU DU DÉFI (écran principal de tous) · ligne 152

## TROISIÈME VAGUE · ligne 182

## THÈME NOËL (défi de décembre) · ligne 225

## PERSONNAGES ANIMÉS DES DÉFIS · ligne 237

## COMPTE À REBOURS DU DÉFI · ligne 312

## MODE TV (salle de sport) · ligne 330

## GARDES · ligne 421

## LE MOT DU SERGENT-CHEF · ligne 449

## OBJECTIF BONUS, VITRINE DES DÉFIS · ligne 466

## ACCUEIL PERSONNALISÉ, CONNEXION · ligne 506

## SUIVI DE LA PARTICIPATION (admin) · ligne 524

## FLAMME, BRAVOS, SERGENT SUR LE NIVEAU · ligne 530

## RECORD, DÉFI DU JOUR, COMPTE À REBOURS, SIMULATEUR · ligne 545

## LA SALLE, PROGRAMMATION, UTILISATION · ligne 570

## DUELS, MUR DES PHOTOS · ligne 588

## DÉCO DE NOËL · ligne 608
- Mode terrain (saisie mobile)

## Séances — habillage visuel + effets (idées validées par Christian le 14/09/2026) · ligne 851

## MÉNAGE · ligne 890

## MON SPORT — l'application de Christian, mise à disposition de la caserne · ligne 942

## DÉFIS COLLECTIFS · ligne 1024

## AIDE · ligne 1105

## SÉANCE DE GARDE (mode TV) · ligne 1140
- Rôle Administrateur
- Comptes secondaires
- Anti-perte de saisie
- Saisie sans réseau

Fonctions : `updateDirtyFlag`, `lireLocal`, `sauverBrouillon`, `effacerBrouillon`, `sauverCache`, `effacerCache`, `proposerBrouillon`, `markDirty`, `clearDirty`, `cleanName`, `loadFromSupabase`, `saveToSupabase`, `updateSupabaseStatus`, `escAttr`, `getAge`, `txtAge`, `getTranche`, `getLevelBadge`, `getAppreciation`, `participationRate`, `getPartClass`, `timeToSec`, `secToTime`, `getTrancheErgo`, `evalRameur`, `evalTest`, `getNiveauGlobal`, `toggleLoginPass`, `doLogin`

## APERÇU « VUE CHEF » (administrateur) · ligne 2131

Fonctions : `choisirApercuChef`, `entrerApercuChef`, `quitterApercu`, `doLogout`, `finaliserConnexion`, `onAuthSuccess`, `tabAutorise`, `applyPermissions`, `resoudreRole`, `showLoginScreen`, `initAuth`, `switchTab`, `switchTabInterne`, `renderAll`, `renderDashboard`, `anneauSvg`, `barreNiveaux`, `comptesNiveaux`, `renderDashboardVisuel`, `parNomPrenom`, `renderSaisie`, `updateField`, `saveAll`, `deletePompier`, `showAddPompier`, `ouvrirModifPompier`, `fermerModifPompier`, `masqueDate`, `chiffresEnDate`, `dateNaissanceTxt`, `lireNaissance`, `lireAnniv`, `validerModifPompier`, `closeModal`, `addPompier`, `creerAccesApresAjout`, `pompiersCampagne`

## SYNTHÈSE CODES COULEUR (pour le chef de centre) · ligne 2426

Fonctions : `badgeHtml`, `iconeTest`, `epreuvesPassees`

## SYNTHÈSE PUBLIÉE (comptes « vue chef ») · ligne 2445

Fonctions : `estChef`, `chargerSynthesePubliee`, `publierSyntheseDiffere`, `publierSynthese`, `syntheseLignes`, `syntheseResume`, `pastilleHtml`, `renderSynthese`

## PLANNING DES SESSIONS ICP · ligne 2535

Fonctions : `chargerSessions`, `aujourdhuiISO`, `sessionsAVenir`, `prochaineSession`, `dateLongue`, `libelleSession`, `testsManquants`, `renderSessions`, `ajouterSession`, `supprimerSession`

## ACCÈS DES POMPIERS · ligne 2602

Fonctions : `renderAccesPompiers`, `aVueChef`, `boutonVueChef`, `basculerVueChef`, `messageAccesPompier`, `creerAccesPompier`, `activerAccesPompier`, `nouveauMdpPompier`, `supprimerAccesPompier`

## TABLEAU DES IDENTIFIANTS · ligne 2691

Fonctions : `chargerMdpProvisoires`, `nomCompte`, `renderIdentifiants`, `messageIdentifiants`, `renvoyerIdentifiants`, `identifiantsPDF`

## MESSAGE DE BIENVENUE · ligne 2763

Fonctions : `afficherBienvenue`, `pastille`, `fermerBienvenue`

## BILAN DE FIN DE CAMPAGNE · ligne 2789

Fonctions : `fermerBilan`, `ouvrirBilanCampagne`, `validerBilanCampagne`, `messageBilanChef`, `messageBilanPompiers`

## RELANCE DES POMPIERS NON ÉVALUÉS · ligne 2853

Fonctions : `genererRelance`

## FICHE INDIVIDUELLE (PDF) · ligne 2866

Fonctions : `dessinerFiche`

## EFFETS VISUELS · ligne 2949

Fonctions : `animerOnglet`, `animerNombre`, `pas`, `confettis`, `vibrer`, `courbeNiveaux`

## DEUXIÈME VAGUE · ligne 2991

Fonctions : `fin`, `cocheSauvegarde`, `badgesFiche`, `jaugeTest`, `jaugeHtml`, `basculerThemeAnime`

## BANDEAU DU DÉFI SUR L'ÉCRAN PRINCIPAL · ligne 3060

Fonctions : `dfsDefiDuBandeau`, `quandContrib`, `renderBandeauDefi`, `ouvrirAjoutDefi`

## MODE TV (télé ou tablette de la salle de sport) · ligne 3113

Fonctions : `estEcran`, `preparerCompteEcran`, `lienAjout`, `qrSvg`, `ouvrirModeTV`, `fermerModeTV`, `tvPleinEcran`, `tvGarderAllume`

## RADIO DE LA SALLE (mode TV) : radios qui bougent, gratuites, en direct · ligne 3159

Fonctions : `radioVoulue`, `radioMemo`, `radioMaj`, `radioHtml`, `radioJouer`, `radioReprendre`, `radioCouper`, `radioBasculer`, `radioChanger`

## LA VIE DE LA SALLE (mode TV) : alerte séance, Sergent-Chef au micro, mode nuit, météo, anniversaires, pompier du mois · ligne 3214
- Le haut-parleur du Sergent-Chef
- Alerte séance en direct
- Le micro : quelques annonces par jour, jamais la nuit
- Mode nuit : 22 h – 6 h, écran sombre et radio coupée (OK sur la télécommande = 30 min de répit)
- Météo de Cruzy et de Quarante (Open-Meteo, gratuit, sans clé, un seul appel pour les deux)

Fonctions : `slugNom`, `sgtNom`, `hmMaintenant`, `personnes`, `annivDe`, `annivsDuJour`, `pompierDuMois`, `titreDuMois`, `deMois`, `moisTitreVisible`, `fetesHtml`, `afficheDuMois`, `radioDucker`, `tvSonPossible`, `sgtDire`, `sonContexte`, `sonCharger`, `jouerSuite`, `sgtSuivant`, `sgtAncien`, `joue`, `hasard`, `tvVerifNouveautes`, `tvAlerteSuivante`, `paliersNouveaux`, `feteBonusAppli`, `sgtAnnonce`, `sgtTic`, `tvEstNuit`, `tvNuitTic`, `tvNuitHtml`, `chargerMeteo`, `meteoIcone`, `meteoConseil`, `meteoHtml`, `fetesTvHtml`, `radioVeille`, `tvAjuster`, `renderTV`

## SÉANCE DE GARDE (mode TV) : séance guidée au poids du corps, Sergent-Chef ou Sergente-Chef à l'écran · ligne 3492
- voix du coach : messages enregistrés (audio/garde/h ou f), la radio baisse pendant qu'il parle
- déroulé

Fonctions : `gardeVid`, `gardeBoutonHtml`, `gardeEl`, `gardeSauver`, `gardeHaut`, `gardeOuvrir`, `gardeRegle`, `gardeFermer`, `gardeMelanger`, `gardePlan`, `gardeTaire`, `gardeDire`, `suivant`, `gardeBip`, `gardeBulle`, `gardePick`, `gardeDemarrer`, `gardeEntrer`, `gardeRestant`, `gardeMajChrono`, `gardeSeconde`, `gardeSuite`, `gardePause`, `gardeArreter`, `gardeTerminer`

## RAME EN DIRECT sur le mode TV : dès qu'un téléphone diffuse une séance de rameur/SkiErg, la télé l'affiche · ligne 3661

Fonctions : `rameEcouter`, `rameOuvrir`, `rameFermer`, `apresChargementDefis`, `dfsAffichetteQR`

## GARDES (défi garde contre garde) · ligne 3736

Fonctions : `normGarde`, `gardeDe`, `listeGardes`, `nomGarde`, `couleurGarde`, `remplirListeGardes`, `dfsGardesStats`, `dfsGardesHtml`, `gardesLigneHtml`, `ouvrirAnnivs`, `majAnniv`, `fermerAnnivs`, `ouvrirGardes`, `fermerGardes`, `ajouterNomGarde`, `choisirGarde`, `renderGardes`

## LE MOT DU SERGENT-CHEF (mascotte du centre) · ligne 3830

Fonctions : `phrasesSergent`, `joursSansSeance`, `humeurSergent`, `cleJourSergent`, `renderMotSergent`, `sergentSuivant`, `taireSergent`

## OBJECTIF BONUS, CARTE « MON DÉFI » ET VITRINE DES MÉDAILLES · ligne 3943

Fonctions : `dfsBonus`, `palierBonus`, `nbPaliersBonus`, `jaugeContenu`, `pctAffiche`, `dfsBonusHtml`, `dfsMonBilan`, `dfsCarteBilan`, `vitrineDefisHtml`

## ACCUEIL PERSONNALISÉ (comptes reliés à un pompier) · ligne 4055

Fonctions : `annivPersoHtml`, `annivPersoEditer`, `annivPersoOk`, `annivPersoEnvoyer`, `renderAccueilPerso`

## FLAMME DE RÉGULARITÉ, BRAVOS, MOT DU SERGENT SUR LE NIVEAU · ligne 4088

Fonctions : `flammeDe`, `flammeHtml`, `chargerBravos`, `dfsBravo`, `dfsSeancesHtml`, `sergentNiveauHtml`

## RECORDS, DÉFI DU JOUR, COMPTE À REBOURS ICP, SIMULATEUR · ligne 4138

Fonctions : `dfsRecord`, `dfsRecordHtml`, `cleCasesLocales`, `casesLocales`, `sauverCasesLocales`, `migrerAnciennesCases`, `chargerCases`, `marquerCase`, `nbDefisJour`, `defiDuJourHtml`, `cocherDefiJour`, `compteReboursIcpHtml`, `simulateurHtml`, `majSimulateur`

## DÉCO DE NOËL (automatique du 1er au 31 décembre) · ligne 4246
- Calendrier de l'Avent
- Grand final du 24 décembre : le traîneau décolle

Fonctions : `estPeriodeNoel`, `bonnetSvg`, `guirlandeHtml`, `appliquerNoel`, `neigeVoulue`, `basculerNeige`, `demarrerNeige`, `taille`, `arreterNeige`, `apercuNoel`, `joursAvantNoel`, `jourAvent`, `jourIsoAvent`, `aventOuvertes`, `renderAvent`, `ouvrirAvent`, `fermerAvent`, `dessinerAvent`, `caseAvent`, `finalNoel`

## AFFICHE ET MESSAGE WHATSAPP DU SERGENT-CHEF (admin, en un clic) · ligne 4373

Fonctions : `dfsPointSituation`, `prenomDe`, `dfsMessageWhatsapp`, `dfsAfficheWhatsapp`

## « MON ANNÉE » (carte à partager, de décembre à fin janvier ; l'admin la voit toute l'année) · ligne 4449

Fonctions : `monAnnee`, `boutonAnneeHtml`, `carteAnnee`

## BADGES DE DÉFI SUR LA FICHE · ligne 4500

Fonctions : `badgesDefis`, `h`

## INSCRIPTIONS AUX SESSIONS ICP (table inscriptions_icp ; places limitées par sessions_icp.places) · ligne 4514

Fonctions : `chargerInscriptions`, `inscritsDe`, `estInscrit`, `basculerInscription`, `inscriptionHtml`

## BILAN DU MOIS POUR LES CHEFS (PDF d'une page, chiffres collectifs uniquement) · ligne 4541

Fonctions : `bilanMoisPDF`

## LA SALLE : MACHINES EN PANNE (table pannes) · ligne 4583

Fonctions : `chargerPannes`, `pannesOuvertes`, `salleHtml`, `ouvrirPanne`, `fermerPanne`, `photoPanne`, `envoyerPanne`, `panneReparee`, `voirPhotoPanne`

## PROGRAMMER LES DÉFIS DE L'ANNÉE (admin) · ligne 4644

Fonctions : `moisAVenir`, `defiDuMois`, `programmeAnneeHtml`, `programmerDefi`, `programmerTout`

## TABLEAU DE BORD D'UTILISATION (admin, onglet Comptes) · ligne 4685

Fonctions : `chargerUtilisation`, `utilisationHtml`

## DUELS (un pompier en défie un autre sur le défi en cours, jusqu'au dimanche) · ligne 4708

Fonctions : `chargerDuels`, `scoreDuel`, `dimancheProchain`, `duelsHtml`, `lancerDuel`, `repondreDuel`

## MUR DES PHOTOS (photo d'une séance, validée par l'admin avant de s'afficher) · ligne 4754

Fonctions : `chargerPhotosSeances`, `photoDeContrib`, `ajouterPhotoSeance`, `retirerPhotoSeance`, `validerPhotoSeance`, `voirPhotoSeance`, `murPhotosHtml`, `tvPhotoHtml`, `feterPalierDefi`

## TROISIÈME VAGUE · ligne 4814

Fonctions : `iconeSvg`, `poserIconesOnglets`

## PERSONNAGES ANIMÉS · ligne 4846

Fonctions : `humeurDefi`, `themeIc`, `iconeDefi`, `personnageHtml`, `IMG_D`, `decorsHtml`

## HUMOUR DES DÉFIS (Noël, Movember) · ligne 4895

Fonctions : `themeHumour`, `phraseDuJour`, `phraseAuHasard`, `sexeDe`, `titreHumour`, `oeufDePaques`

## THÈME NOËL : « Aidons le Père Noël à skier » · ligne 4932

Fonctions : `estNoel`, `neigeHtml`, `etapeNoel`, `estMovember`, `bateauHtml`, `chargerPhotos`, `avatarMini`, `initialesDe`, `peutChangerPhoto`, `choisirPhoto`, `retirerPhoto`, `majPastilleDefis`, `etatVide`, `pdfEntete`

## OBJECTIFS ET ÉVOLUTION PAR TEST · ligne 5008

Fonctions : `seuilsRameur`, `niveauTest`, `nombreFr`, `objectifTest`, `niveauPrecedentTest`, `evolutionTest`, `evolutionCampagne`

## PROGRAMME D'ENTRAÎNEMENT PERSONNALISÉ · ligne 5063

Fonctions : `allureKmh`, `tempsSur`, `construireProgramme`, `poids`, `texteNiveauCourt`, `renderProgramme`, `textePdf`, `programmePDF`, `renderFiche`, `ficheExportPDF`

## JOURNAL DES MODIFICATIONS (administrateur) · ligne 5255

Fonctions : `chargerJournal`, `vide`, `generateFichePDF`, `generateToutesFichesPDF`, `generateSynthesePDF`, `presence`, `renderBilan`, `getNiveauGlobal`, `getAge`, `renderEchelles`

## ZONES CARDIO — méthode FC Réserve (Karvonen) · ligne 5412

Fonctions : `getFcMax`, `getFcRepos`, `vo2maxRameur`, `setCardioField`, `reprendrePompierCalc`, `renderCalcVo2`, `renderCardio`

## VMA et VO2max estimés à partir du test Luc Léger · ligne 5540

Fonctions : `vmaLuc`, `vo2maxLuc`

## HISTORIQUE DES CAMPAGNES · ligne 5556
- Vue « une campagne, tous les pompiers »
- Vue « un pompier, son historique »

Fonctions : `chargerHistoriqueReferenceDistant`, `getHistorique`, `setHistorique`, `aDesDonnees`, `normNom`, `fusionnerHistoriqueImport`, `chargerHistoriqueDeReference`, `importerHistorique`, `cloturerCampagne`, `archiverCampagne`, `deltaHtml`, `deltaTempsHtml`, `listeCampagnes`, `ligneCampagne`, `lignesTriees`, `celluleEvo`, `renderProgression`

## MODE TERRAIN (saisie mobile, un pompier à la fois) · ligne 5788

Fonctions : `terrainStep`, `normaliserSaisie`, `niveauChamp`, `terrainChamps`, `terrainPompierCourant`, `libelleOptionTerrain`, `majTerrainProgression`, `renderTerrain`, `terrainMaj`, `focusPremierVide`, `terrainEntree`, `renderAtelier`, `vide`, `atelierMaj`

## MUSCULATION — 1 RM et charges d'entraînement · ligne 5930

Fonctions : `effetPourReps`, `coefBrzycki`, `rmBrzycki`, `rmPoliquin`, `polarPt`, `sectorPath`, `midArcPath`, `renderMuscuGauge`, `renderMuscu`, `generateMuscuPDF`

## SÉANCES EN GARDE — « Développer la force musculaire, quelques repères » (CNFPT) · ligne 6094

## FICHE DE SEANCE — nouveau rendu (pictogrammes uniformises, photos perso Cross Training) · ligne 6120

Fonctions : `getRpeRange`, `isCircuit`, `getMateriel`, `iconeMateriel`, `iconeSeance`, `classeNiveau`, `rpeGaugeHtml`, `animateRpeThermos`, `pdfRpeGauge`

## EMOM à 3 niveaux (fiche fixe, indépendante du générateur de séance) · ligne 6231

Fonctions : `renderEmom`, `generateEmomPDF`, `pdfSectionTitle`, `drawExerciseGrid`

## GÉNÉRATEUR DE SÉANCE — Livret des ressources, formation EAP2 (CNFPT) · ligne 6355

Fonctions : `showToast`, `tirerSeance`, `alea`, `choisirZoneExercice`, `getExerciceZone`

## Carnet de suivi (idee #3) : persistance des entrees RPE / charge de seance (UA) par pompier · ligne 6498

## MON SPORT (l'application de Christian, mise à disposition de la caserne) · ligne 6500
- effets repris de mon-app-sport
- rendu
- Participation du centre (administrateur) et point faible ICP
- Notifications poussées (elles arrivent même application fermée)

Fonctions : `sptMoi`, `sptEsc`, `sptCharger`, `sptMarquerVu`, `sptRevoir`, `sptReduit`, `sptEnterFx`, `sptSlide`, `renderProgramme`, `sptAller`, `sptFil`, `sptAccueil`, `sptCadre`, `sptChargerPart`, `sptCarteParticipation`, `sptPointFaible`, `sptCartePointFaible`, `pushDispo`, `pushB64`, `pushCharger`, `pushActiver`, `pushCouper`, `pushRegler`, `pushToggleJour`, `pushCarte`

## AIDE · ligne 6818

Fonctions : `aideEsc`, `aideMoi`, `aideBascule`, `aideBloc`, `renderAide`

## DÉFIS COLLECTIFS · ligne 6931
- rendu

Fonctions : `dfsEsc`, `dfsMoi`, `dfsTheme`, `chargerAnnuaire`, `dfsNom`, `dfsNum`, `dfsRythme`, `dfsIso`, `chargerDefis`, `dfsStats`, `dfsAVenir`, `dfsVisibles`, `dfsJoursAvant`, `dfsTexteAnnonce`

## SCÈNE DE NOËL : « Aidons le Père Noël à skier » · ligne 7034
- les gags
- Branchement de la scène de Noël : télé (à la place de la jauge) et onglet Défis (sous la jauge)
- Rame en direct : le Sergent-Chef rame avec toi (page rame.html, rameur Concept2 PM5 ou SkiErg en Bluetooth)
- actions

Fonctions : `SceneNoel`, `R`, `chaine`, `piste`, `taille`, `img`, `ciel`, `montagnes`, `sol`, `trace`, `decors`, `skieur`, `particules`, `neige`, `bonnetSur`, `bonhommeNeige`, `lancerGag`, `dessinerBulle`, `feuArtifice`, `image`, `noelImages`, `noelCoach`, `noelSceneHtml`, `noelBrancher`, `noelPct`, `lienRame`, `estIphoneSansBT`, `rameCopier`, `ok`, `rameCarteHtml`, `renderDefis`, `dfsVoir`, `dfsCarte`, `dfsSuiviHtml`, `nom`, `bloc`, `dfsCopierRelance`, `dfsAdminHtml`, `dfsMesLignes`, `dfsAjouter`, `dfsRetirer`, `dfsNouveau`, `dfsModifier`, `dfsAnnuler`, `dfsSetTheme`, `dfsSetCouleur`, `dfsLireForm`, `dfsFormulaire`, `dfsEnregistrer`, `dfsBasculer`, `dfsSupprimer`, `dfsAffiche`

## PODIUM DE LA SEMAINE (régularité) · ligne 7497

Fonctions : `dfsLundi`, `dfsSemaine`, `dfsLibSemaine`, `f`, `dfsPodium`, `dfsPodiumHtml`, `bloc`

## AFFICHE FINALE (PDF, avec photo de groupe facultative) · ligne 7535

Fonctions : `illuPourPdf`, `dfsAfficheFinale`, `dfsTextePdf`, `dfsAfficheFinalePdf`

## COMPTE À REBOURS DU DÉFI · ligne 7604

Fonctions : `dfsCompteurDonnees`, `dfsCompteurHtml`, `dfsChrono`, `p`, `dfsCompteurTick`

## DIPLÔMES DE FIN DE DÉFI (PDF A4 paysage) · ligne 7646

Fonctions : `dfsDiplomeClassement`, `dfsDiplomeReglages`, `dfsDiplomeTexte`, `dfsDiplomeRang`, `dfsDiplomeMoustache`, `dfsDiplomeMedaille`, `dfsDiplomePage`, `dfsDiplomePdf`, `dfsDiplomeEditeurHtml`, `dfsDiplomeLireForm`, `g`, `dfsDiplomeApercu`, `dfsDiplomeEnregistrer`, `dfsMonDiplome`, `dfsTousDiplomes`, `dfsEnterFx`

## MÉNAGE (planning de nettoyage de la salle) · ligne 7777
- Bloc « aujourd'hui » : je coche ma mission
- Statistiques
- Grille du mois (saisie de la feuille papier, administrateur)

Fonctions : `menEsc`, `menMission`, `menIniDe`, `menIniValide`, `menTokens`, `menCouleur`, `menPastille`, `menDateCle`, `menSansAccent`, `menageMoi`, `menageChoisirMoi`, `menageChangerMoi`, `menageSelectQui`, `nomPourInitiales`, `chargerMenage`, `menagePeriode`, `renderMenage`, `renderMenageAujourdhui`, `basculerMaMission`, `menageStats`, `renderMenagePodium`, `renderMenageZones`, `renderMenageGrille`, `menageSaisie`, `menNormaliserCode`, `menageParseCase`, `enregistrerMenage`, `exporterMenagePDF`, `chargerCarnetSiBesoin`, `majCarnetUA`, `step`, `ajouterCarnetEntree`, `sparklineSvg`, `renderCarnetHistorique`, `zoneSelectHtml`, `catalogueSeances`, `majObjectifs`, `renderSeance`

## Matériel · ligne 8317

## Outil de suivi RPE / Borg · ligne 8324

## Tableau des 3 niveaux (séances de type Circuit uniquement) · ligne 8335

## Règles à ne jamais oublier + Repères de récupération (toutes les séances de musculation) · ligne 8434

Fonctions : `pdfLogo`, `chargerImagesPdf`, `generateSeancePDF`, `genererSeancePDF`, `checkPage`, `togglePPA`, `renderPPA`, `renderExport`, `copyExport`, `importData`

## PDF — zones cardio · ligne 8735
- Taux de participation
- Répartition des niveaux, avec les noms
- Résultats détaillés (uniquement les pompiers évalués)

Fonctions : `hexToRgb`, `tintRgb`, `cardioRows`, `generateCardioPDF`, `generateBilanPDF`, `age`, `generatePDF`

## EN-TÊTE · ligne 8918

## STATISTIQUES GLOBALES · ligne 8937

## TABLEAU DES POMPIERS · ligne 8967
- Interface : en-tête, menu du compte, thème, navigation téléphone
- Mon mot de passe (tout compte connecté)
- Gestion des comptes secondaires (onglet Comptes, admin uniquement)

Fonctions : `gradeComplet`, `nomGrade`, `galonSvg`, `afficherCompteEntete`, `basculerMenuCompte`, `fermerMenuCompte`, `majBoutonTheme`, `basculerTheme`, `infoOnglet`, `ongletsVisibles`, `ongletActif`, `construireNavBas`, `majNavActive`, `ouvrirPlus`, `ouvrirGroupe`, `fermerPlus`, `ouvrirMonMdp`, `fermerMonMdp`, `changerMonMdp`, `appelerGererComptes`, `chargerComptes`, `checkboxesOnglets`, `ongletsCoches`

## CONNEXIONS · ligne 9217
- Envoi du lien et des identifiants (email, SMS, WhatsApp, copier)
- Carte d'accès (image PNG) à envoyer par WhatsApp : emblème, lien, identifiant, mot de passe
- Visuels à partager (WhatsApp) : session ICP et carte de résultats individuelle

Fonctions : `chargerConnexions`, `quandLisible`, `jour`, `badgeConnexion`, `nomPourEmail`, `renderConnexions`, `renderComptes`, `genererMotDePasse`, `lienAppli`, `ouvrirMessage`, `ouvrirEnvoi`, `fermerEnvoi`, `chargerImageCarte`, `rectArrondi`, `genererCarteAcces`, `cartesAccesPDF`, `scanConnexionDirecte`, `afficherCarteScan`, `fermerScan`, `diffuserImage`, `lignesTexte`, `baseCarteVisuelle`, `pilule`, `versBlob`, `genererVisuelSession`, `partagerVisuelSession`, `genererCarteResultat`, `partagerCarteResultat`, `partagerCarte`, `envoyerAcces`, `sauverCompteExistant`, `ajouterOuMajCompte`, `supprimerCompte`

# rame.html : 10 sections, 58 fonctions

## RENDU · ligne 112

Fonctions : `appliquerQualite`, `redim`

## DÉCOR · ligne 138

Fonctions : `toon`, `contour`, `fabriquerBateau`

## Le Sergent-Chef en 3D (style cartoon, contours noirs), face à la poupe (+z) · ligne 165

Fonctions : `M`, `seg`, `rot`, `chaussure`, `texSillage`

## PERSONNAGES MODÉLISÉS (Blender, avec squelette) · ligne 255

Fonctions : `contourMat`, `habiller`, `viser`, `chargerPerso`, `poserPerso`, `choisirPerso`, `texGoutte`, `eclabousser`, `panneauTexte`, `fabriquerPhare`, `fabriquerIle`

## DONNÉES (simulation ou PM5) · ligne 357
- PM5 Concept2 en Bluetooth (service « rowing » du PM5)
- Diagnostic Bluetooth : montre tous les appareils, puis la liste des services de celui qu'on choisit

Fonctions : `simuler`, `decrireErr`, `demanderMachine`, `etatBluetooth`, `journalHtml`, `messageBT`, `connecterPM5`, `connecterFTMS`, `lireCrossTrainer`, `diagnosticBT`

## SERGENT-CHEF · ligne 497

Fonctions : `ditSergent`

## LES TRUCS LOUFOQUES · ligne 503
- 1) Le camion de pompiers flottant : il croise le bateau, gyrophares et pin-pon
- 2) La mouette squatteuse : elle se pose sur le casque, il faut accélérer pour la faire fuir
- 3) La douche surprise : immobile 10 secondes, une vague l'arrose

Fonctions : `bip`, `pinPon`, `plouf`, `cri`, `fabriquerCamion`, `toile`, `fabriquerMouette`, `teteMonde`, `douche`, `loufoque`

## ANIMATION · ligne 599

Fonctions : `demarrer`, `placerPhare`, `fmt`, `boucle`, `ease`, `poser`, `deuxOs`, `ikMembres`, `animerRameur`, `majHud`, `finir`

## COMMANDES · ligne 710

## EN DIRECT SUR LA TÉLÉ DE LA SALLE · ligne 724
- côté téléphone
- côté télé

Fonctions : `lienPage`, `qrHtml`, `diffuserPret`, `envoyer`, `retourAttente`
