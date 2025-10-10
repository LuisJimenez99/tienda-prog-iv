from django.db import migrations

# Lista de 30 recetas saludables con ingredientes argentinos
RECETAS = [
    {
        "nombre": "Guiso de Lentejas Nutritivo",
        "ingredientes": "Lentejas, cebolla, morrón, zanahoria, papa, batata, zapallo, carne magra (opcional), tomate triturado, pimentón, comino, ají molido, laurel.",
        "instrucciones": "Remojar las lentejas. Saltear vegetales picados. Agregar la carne si se usa. Incorporar lentejas, puré de tomate, agua y condimentos. Cocinar a fuego bajo hasta que todo esté tierno.",
        "tiempo_preparacion": "1 hora 30 minutos",
    },
    {
        "nombre": "Milanesas de Berenjena al Horno",
        "ingredientes": "Berenjenas, huevo, avena, pan rallado integral, ajo en polvo, perejil, queso port salut light.",
        "instrucciones": "Cortar las berenjenas en rodajas. Pasarlas por huevo batido y luego por la mezcla de avena, pan rallado y condimentos. Colocar en una placa para horno aceitada y cocinar hasta que estén doradas. Gratinar con queso.",
        "tiempo_preparacion": "40 minutos",
    },
    {
        "nombre": "Zapallitos Rellenos de Quinoa",
        "ingredientes": "Zapallitos redondos, quinoa, cebolla, morrón, zanahoria, choclo, queso cremoso light, nuez moscada.",
        "instrucciones": "Hervir los zapallitos y ahuecarlos. Cocinar la quinoa. Saltear los vegetales picados, mezclarlos con la pulpa de los zapallitos y la quinoa. Rellenar, agregar un trozo de queso y gratinar al horno.",
        "tiempo_preparacion": "50 minutos",
    },
    {
        "nombre": "Tarta de Espinaca y Ricota con Masa Integral",
        "ingredientes": "Espinaca, ricota magra, cebolla, huevo, queso rallado, nuez moscada, masa para tarta integral.",
        "instrucciones": "Saltear la cebolla y la espinaca. Mezclar con la ricota, el huevo y los condimentos. Verter sobre la masa en una tartera y cocinar en horno medio hasta que el relleno esté firme y la masa dorada.",
        "tiempo_preparacion": "1 hora",
    },
    {
        "nombre": "Ensalada Completa de Garbanzos",
        "ingredientes": "Garbanzos cocidos, tomate, pepino, cebolla morada, atún al natural, huevo duro, aceitunas, perejil.",
        "instrucciones": "Picar todos los vegetales y el huevo. Mezclar con los garbanzos y el atún escurrido. Condimentar con aceite de oliva, limón y sal.",
        "tiempo_preparacion": "20 minutos",
    },
    {
        "nombre": "Budín de Calabaza y Avena",
        "ingredientes": "Calabaza asada, huevo, avena instantánea, queso port salut light, cebolla de verdeo, polvo de hornear.",
        "instrucciones": "Hacer un puré con la calabaza. Mezclar con los huevos, la avena, el queso en cubos, la cebolla de verdeo picada y el polvo de hornear. Verter en una budinera y cocinar en horno medio.",
        "tiempo_preparacion": "55 minutos",
    },
    {
        "nombre": "Pollo al Limón con Batatas Asadas",
        "ingredientes": "Pechuga de pollo, limones, batatas, romero, tomillo, ajo, aceite de oliva.",
        "instrucciones": "Marinar el pollo con jugo de limón, hierbas y ajo. Cortar las batatas en bastones. Colocar todo en una fuente para horno y cocinar hasta que el pollo esté cocido y las batatas tiernas y doradas.",
        "tiempo_preparacion": "1 hora 10 minutos",
    },
    {
        "nombre": "Wok de Vegetales y Arroz Integral",
        "ingredientes": "Arroz integral, brócoli, zanahoria, morrón, zucchini, cebolla, brotes de soja, salsa de soja baja en sodio.",
        "instrucciones": "Cocinar el arroz integral. Cortar todos los vegetales en juliana y saltearlos en un wok caliente. Agregar el arroz cocido y la salsa de soja. Integrar bien.",
        "tiempo_preparacion": "35 minutos",
    },
    {
        "nombre": "Tortilla de Acelga al Horno",
        "ingredientes": "Acelga, cebolla, huevo, avena, queso rallado.",
        "instrucciones": "Hervir y picar la acelga. Saltear la cebolla. Mezclar todo con los huevos batidos, la avena y el queso. Verter en una fuente para horno aceitada y cocinar hasta que esté firme.",
        "tiempo_preparacion": "45 minutos",
    },
    {
        "nombre": "Pastel de Papa y Calabaza Saludable",
        "ingredientes": "Carne picada magra, cebolla, morrón, huevo duro, puré de papas, puré de calabaza, nuez moscada.",
        "instrucciones": "Hacer un relleno salteando la carne con los vegetales. Colocar en una fuente con el huevo duro picado. Cubrir con el puré mixto de papa y calabaza. Gratinar al horno.",
        "tiempo_preparacion": "1 hora 15 minutos",
    },
    {
        "nombre": "Hamburguesas de Lentejas",
        "ingredientes": "Lentejas cocidas, cebolla, ajo, perejil, avena, comino.",
        "instrucciones": "Procesar las lentejas con los vegetales y condimentos. Agregar avena hasta formar una masa manejable. Dar forma de hamburguesas y cocinar a la plancha o al horno.",
        "tiempo_preparacion": "30 minutos",
    },
    {
        "nombre": "Sopa Crema de Zanahoria y Jengibre",
        "ingredientes": "Zanahorias, cebolla, papa, jengibre fresco, caldo de verduras casero, queso crema light.",
        "instrucciones": "Hervir los vegetales en el caldo hasta que estén tiernos. Procesar con un mixer hasta obtener una crema. Servir con una cucharada de queso crema.",
        "tiempo_preparacion": "40 minutos",
    },
    {
        "nombre": "Revuelto Gramajo Fit",
        "ingredientes": "Pechuga de pavo o pollo, papas al horno en bastones, arvejas, huevo, cebolla de verdeo.",
        "instrucciones": "Saltear el pollo en juliana. Agregar las papas ya cocidas, las arvejas y la cebolla de verdeo. Echar los huevos batidos y revolver hasta que cuajen.",
        "tiempo_preparacion": "25 minutos",
    },
    {
        "nombre": "Pescado a la Plancha con Puré de Coliflor",
        "ingredientes": "Filet de merluza, limón, perejil, ajo, coliflor, leche descremada, nuez moscada.",
        "instrucciones": "Cocinar el pescado a la plancha con limón y ajo. Hervir la coliflor y procesarla con un poco de leche y nuez moscada hasta obtener un puré cremoso.",
        "tiempo_preparacion": "30 minutos",
    },
    {
        "nombre": "Humita a la Olla",
        "ingredientes": "Choclo rallado o procesado, zapallo, cebolla, morrón, leche descremada, albahaca.",
        "instrucciones": "Rallar el choclo y el zapallo. Saltear la cebolla y el morrón. Unir todo en una olla, agregar un poco de leche y cocinar revolviendo hasta que espese. Terminar con albahaca fresca.",
        "tiempo_preparacion": "50 minutos",
    },
    {
        "nombre": "Canelones de Verdura con Salsa Fileto",
        "ingredientes": "Panqueques integrales, acelga, ricota magra, salsa de tomate casera, queso port salut light.",
        "instrucciones": "Mezclar la acelga cocida con la ricota para el relleno. Armar los canelones. Colocar en una fuente, cubrir con salsa de tomate y queso. Gratinar.",
        "tiempo_preparacion": "1 hora",
    },
    {
        "nombre": "Ensalada Tibia de Brócoli y Pollo",
        "ingredientes": "Brócoli, pechuga de pollo grillada, almendras tostadas, cebolla morada, aderezo de yogur natural y limón.",
        "instrucciones": "Cocinar el brócoli al vapor. Cortar el pollo en cubos. Mezclar con la cebolla en pluma y las almendras. Aderezar.",
        "tiempo_preparacion": "25 minutos",
    },
    {
        "nombre": "Albóndigas de Carne y Avena en Salsa",
        "ingredientes": "Carne picada magra, avena, huevo, perejil, salsa de tomate casera, zanahoria rallada.",
        "instrucciones": "Mezclar la carne con avena, huevo y perejil para formar las albóndigas. Cocinarlas dentro de la salsa de tomate con zanahoria rallada a fuego bajo.",
        "tiempo_preparacion": "45 minutos",
    },
    {
        "nombre": "Polenta con Estofado de Champiñones",
        "ingredientes": "Polenta instantánea, champiñones, cebolla, ajo, vino blanco (opcional), puré de tomate, hierbas.",
        "instrucciones": "Preparar la polenta. Aparte, saltear cebolla, ajo y champiñones. Desglasar con vino, agregar tomate y hierbas. Cocinar 15 minutos. Servir sobre la polenta.",
        "tiempo_preparacion": "30 minutos",
    },
    {
        "nombre": "Matambre a la Pizza Saludable",
        "ingredientes": "Matambre de ternera o cerdo, salsa de tomate, queso port salut light, rodajas de tomate, orégano, aceitunas.",
        "instrucciones": "Hervir el matambre hasta que esté tierno. Colocar en una placa para horno, cubrir con salsa, queso, tomate y condimentos. Gratinar.",
        "tiempo_preparacion": "2 horas (incluye hervor)",
    },
    {
        "nombre": "Muffins de Banana y Avena (Sin Azúcar)",
        "ingredientes": "Bananas maduras, huevo, avena, polvo de hornear, canela, nueces (opcional).",
        "instrucciones": "Pisar las bananas. Mezclar con el huevo, la avena, el polvo de hornear y la canela. Agregar nueces si se desea. Verter en moldes para muffins y hornear.",
        "tiempo_preparacion": "30 minutos",
    },
    {
        "nombre": "Salpicón de Atún y Arroz Integral",
        "ingredientes": "Arroz integral cocido, atún al natural, arvejas, zanahoria hervida en cubos, morrón picado, mayonesa light.",
        "instrucciones": "Mezclar todos los ingredientes fríos. Integrar con la mayonesa light. Servir frío.",
        "tiempo_preparacion": "15 minutos",
    },
    {
        "nombre": "Tarta de Pollo y Puerros",
        "ingredientes": "Pechuga de pollo hervida y desmenuzada, puerros, cebolla, queso crema light, huevo, masa integral.",
        "instrucciones": "Saltear el puerro y la cebolla. Mezclar con el pollo, el queso crema y el huevo. Verter sobre la masa y hornear.",
        "tiempo_preparacion": "1 hora",
    },
    {
        "nombre": "Bifes a la Criolla Ligeros",
        "ingredientes": "Bifes de nalga o bola de lomo, cebolla, morrón, tomate, caldo de verduras.",
        "instrucciones": "Sellar los bifes. Retirar y en la misma olla saltear los vegetales en juliana. Volver a poner los bifes, agregar el tomate y el caldo. Cocinar a fuego bajo hasta que la carne esté tierna.",
        "tiempo_preparacion": "1 hora",
    },
    {
        "nombre": "Ensalada Rusa Fit",
        "ingredientes": "Papa, zanahoria, arvejas, huevo duro, mayonesa de zanahoria casera o yogur natural.",
        "instrucciones": "Hervir las papas y zanahorias en cubos. Mezclar con las arvejas y el huevo picado. Aderezar con la opción saludable elegida.",
        "tiempo_preparacion": "40 minutos",
    },
    {
        "nombre": "Carbonada Saludable",
        "ingredientes": "Carne magra en cubos, zapallo, choclo, batata, cebolla, duraznos orejones (opcional).",
        "instrucciones": "Sellar la carne. Saltear la cebolla. Agregar los demás vegetales en cubos, caldo y cocinar a fuego bajo. Si se usan, agregar los orejones al final.",
        "tiempo_preparacion": "1 hora 45 minutos",
    },
    {
        "nombre": "Pizza Integral de Vegetales",
        "ingredientes": "Harina integral, levadura, salsa de tomate, zucchini, berenjena, champiñones, rúcula, queso port salut.",
        "instrucciones": "Hacer una masa de pizza con harina integral. Cubrir con salsa, queso y los vegetales grillados. Hornear. Terminar con rúcula fresca.",
        "tiempo_preparacion": "45 minutos",
    },
    {
        "nombre": "Niños Envueltos de Acelga",
        "ingredientes": "Hojas de acelga grandes, carne picada magra, arroz integral, cebolla, salsa de tomate.",
        "instrucciones": "Blanquear las hojas de acelga. Mezclar la carne con arroz y cebolla para el relleno. Armar los paquetitos y cocinarlos en la salsa de tomate.",
        "tiempo_preparacion": "1 hora",
    },
    {
        "nombre": "Sopa de Verduras y Fideos de Lenteja",
        "ingredientes": "Apio, puerro, zanahoria, zapallo, caldo de verduras, fideos de legumbres.",
        "instrucciones": "Hervir los vegetales picados en el caldo. Cuando estén tiernos, agregar los fideos y cocinar por el tiempo que indique el paquete.",
        "tiempo_preparacion": "35 minutos",
    },
    {
        "nombre": "Cazuela de Mondongo Vegetariana",
        "ingredientes": "Garbanzos, porotos, champiñones, cebolla, morrón, tomate triturado, chorizo colorado vegano (opcional).",
        "instrucciones": "Remojar las legumbres. Saltear los vegetales y champiñones. Agregar las legumbres, tomate, condimentos y caldo. Cocinar a fuego bajo hasta que todo esté tierno.",
        "tiempo_preparacion": "2 horas",
    },
]

def cargar_recetas(apps, schema_editor):
    Receta = apps.get_model('recetas', 'Receta')
    for receta_data in RECETAS:
        Receta.objects.create(**receta_data)

class Migration(migrations.Migration):

    dependencies = [
        ('recetas', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(cargar_recetas),
    ]
