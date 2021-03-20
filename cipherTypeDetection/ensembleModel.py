import tensorflow as tf
import pickle
import numpy as np
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.metrics import SparseTopKCategoricalAccuracy
from tensorflow.keras.preprocessing.sequence import pad_sequences
import cipherTypeDetection.config as config
from cipherTypeDetection.transformer import MultiHeadSelfAttention, TransformerBlock, TokenAndPositionEmbedding
from cipherImplementations.cipher import OUTPUT_ALPHABET
from util.utils import get_model_input_length


f1_ffnn = [0.45677661403783026, 0.6785499002923047, 1.0, 0.993867867812318, 0.8442286424167134, 0.5859076061595894, 0.30304328628519256, 0.9999799875923071, 0.26127273287396924, 0.4356883869292373, 0.5628798503973819, 0.6365134538251727, 0.8085363984906851, 0.9979876611449238, 0.9999815267523414, 0.9373136806630701, 0.999351508551307, 0.8604875305036136, 0.975091061571391, 1.0, 0.9947203345530581, 0.9999568946937368, 0.9999368882198014, 0.2855991819640417, 0.6042709689898346, 1.0, 0.2903793343132898, 1.0, 1.0, 0.9993523086887558, 0.6686556020372472, 0.6280907431733375, 0.9829106652600341, 0.7705406903091276, 1.0, 0.9798411160627786, 0.9590404556960498, 0.46540219383538745, 0.17843291311024606, 0.22803008293473345, 0.17494245437019557, 0.1342144970538898, 0.9908008574794165, 0.10341683374632446, 0.1758700204857212, 1.0, 1.0, 0.6083905937622659, 0.8171821406584385, 0.5708910436767174, 0.9999984605887633, 0.6361915536398225, 0.9999799879003768, 0.7745224829365815, 0.43112259993459673, 0.408220433274429, 0.7241931848170303, 0.7178278933865777]
f1_cnn = [0.2501637570130721, 0.22444447408434923, 0.9998911638071771, 0.7427063271274699, 0.029028132992327368, 0.3049749987820487, 0.16121204688403387, 0.4449302775700524, 0.7453429563902737, 0.06448709630156771, 0.2716919803562105, 0.5318055185445384, 0.47970328686532804, 0.5833735202700562, 0.9579247073710851, 0.9547832331192706, 0.5280850813993475, 0.5169099423580541, 0.8863077269655327, 0.46073959216053945, 0.4740977881257276, 0.5519850699083186, 0.8594820696808421, 0.057504991012624955, 0.09944653944508705, 0.9610746543858962, 0.2342837002208278, 0.9991684480454176, 0.9998214899925548, 0.49261715855487886, 0.3366826681455037, 0.33351480045874893, 0.6297257393405218, 0.30029317221263174, 0.36014159292035397, 0.17498199304069065, 0.5174444488275505, 0.14085682492581603, 0.05373314667115895, 0.0023851195991626342, 0.007779067838779233, 0.05214443085901275, 0.9480176287665486, 0.1304362408604074, 0.06875460472357757, 0.999995646135292, 1.0, 0.8487010924020626, 0.10836775004489135, 0.7652524591950735, 0.4253598372360456, 0.5570818098512961, 0.412645871683583, 0.36228229494372916, 0.02773750776635935, 0.005676951242043031, 0.47029858312185896, 0.45424965052545285]
f1_transformer = [0.7351407083406276, 0.5024584551603138, 0.999976002938717, 0.9882868004975551, 0.6596641527489805, 0.6161282389588488, 0.4159959444556888, 0.8656304978764889, 0.8549482161790868, 0.2718754463443011, 0.5705715371920671, 0.6867535907565137, 0.8476727275613579, 0.9720997783733496, 0.9726654074522598, 0.9807870473310505, 0.5674218547771316, 0.8618971832121651, 0.9744780017712664, 0.745762218567992, 0.9805868155408181, 0.9574328015351644, 0.96597497625573, 0.38825748910712027, 0.5155784789543895, 0.9931974551524281, 0.777932328394902, 0.9999446239040148, 0.9999843093965487, 0.5718709023393166, 0.779547870296252, 0.7381405066544782, 0.9919473367865475, 0.7935781225752733, 0.8185463608380189, 0.7362880728669596, 0.837692311441769, 0.3469364611787845, 0.10985741713415935, 0.17404339134452865, 0.12732880257512044, 0.05943488456795251, 0.9907054504210902, 0.6250721180682499, 0.23671620710345082, 0.9999649277604159, 1.0, 0.8678748411719838, 0.6462223616034533, 0.8871314775493201, 0.9639173923014893, 0.6400525938271567, 0.681654611595747, 0.7728284748744043, 0.08237056406179681, 0.4676007046333632, 0.721930049524794, 0.707436200969785]
f1_lstm = [0.7546788431001367, 0.2869263791780175, 0.9999948276129605, 0.9910436432637572, 0.13178104192979995, 0.5619396040568551, 0.4497857707470081, 0.8367248759555722, 0.8095918454386488, 0.21290009283724917, 0.4992885463715865, 0.6674114097952015, 0.8701387658292553, 0.9854074483459371, 0.9787240561661766, 0.9886605256808805, 0.5652650592508013, 0.7608211033329437, 0.9796914644574345, 0.9697052848209811, 0.9873755318984192, 0.9913956450159972, 0.9746956945120678, 0.4420648777453897, 0.45533756036842066, 0.9950670916839358, 0.4572767381350736, 0.9999844829994017, 0.9999896552080856, 0.5772520986827228, 0.71738318978789, 0.6349625476427244, 0.9809172777518157, 0.8478376657962767, 0.9719821792389826, 0.45847572807906545, 0.8905762308800816, 0.32846820127974896, 0.04994122622958023, 0.11062511390559504, 0.08011805426181767, 0.06879382598232439, 0.9911797665637984, 0.6991473339173189, 0.35871086295851295, 0.9999982758650416, 1.0, 0.8705766897437727, 0.7087016210791794, 0.934611409548178, 0.9856174081526194, 0.6651596395910444, 0.6524281351192833, 0.7920249688741835, 0.1329165359145807, 0.14279515402288162, 0.6940798029556651, 0.6831226608322681]
f1_rf = [0.6983374530186571, 0.7262258967675119, 1.0, 0.9321092598889267, 0.804019150271181, 0.4984914793448711, 0.26343459564433347, 1.0, 0.23902292177353462, 0.3447929833363888, 0.45988829756607147, 0.6193573033299072, 0.6340825072790919, 0.9828531594562658, 0.9959304222401566, 0.9554218059791458, 0.9979527137340947, 0.7051409059292202, 0.9756360328856156, 0.999517416107961, 0.9795506444412134, 0.9979702709472357, 0.9912128957854603, 0.14176374314046405, 0.5172820502568819, 0.9996466766056825, 0.27422308507855203, 1.0, 1.0, 0.9979610623123446, 0.5344581687425989, 0.5297705444550816, 0.9843204813166248, 0.8913576242476665, 1.0, 0.9691443753396534, 0.8427958954697101, 0.4270827465780431, 0.13554735547355473, 0.14332736872335253, 0.13723556333735967, 0.14508313642649476, 0.9907847309679941, 0.19680456664601378, 0.20823948681397006, 1.0, 1.0, 0.8357394869838848, 0.749828202308961, 0.5862487159000114, 0.99519359839267, 0.5966697677950977, 0.9999310392386732, 0.6467812770403749, 0.36166194523135037, 0.3579708085503745, 0.7075661945812808, 0.6963893146267909]
f1_nb = [0.6746516145809431, 0.3997535780684481, 0.9999917109440405, 0.9154674514115707, 0.024014769373900655, 0.33572291880022515, 0.25221888868054254, 0.4741214057507987, 0.37276827960381054, 0.1119485120701041, 0.388563464930427, 0.6524363032179662, 0.4975744873095694, 0.7163007595170487, 0.9431926571075634, 0.5610720138821942, 0.6079695251213292, 0.5342282746880993, 0.957231269232099, 0.8617019482162436, 0.5741844099197339, 0.9414446175289005, 0.8800779443820597, 0.26391643114782254, 0.3622901952705008, 0.976060601155695, 0.25915228714606636, 0.9820505515079979, 0.9993621445198274, 0.754417544782207, 0.42152802631354697, 0.4465866641124232, 0.9103206639034126, 0.4998922524852198, 0.9056603773584905, 0.2116070355382828, 0.7590205162144276, 0.2724889222796339, 0.024146765216879175, 0.03523341794503918, 0.04017123054970442, 0.04719510607835481, 0.9906531136815049, 0.20685038268619732, 0.215986860114974, 0.5824136565960857, 0.3037579983326657, 0.34440849472516794, 0.4425965420310839, 0.3676760306457497, 0.8179829422252205, 0.3434920066046309, 0.5776690024115418, 0.5223688839265229, 0.03389783260157502, 0.036861707207268654, 0.5339442615574082, 0.5113277319938098]
accuracy_ffnn = [0.9864353338318086, 0.9910578487860662, 1.0, 0.9997812939831104, 0.9943470707248416, 0.984875637755102, 0.9590390789936665, 0.9999992852744546, 0.984179714989444, 0.9776583941766361, 0.9837045324595355, 0.9874492544862773, 0.9930619392153414, 0.9999281425932441, 0.9999993402533427, 0.9977583457952146, 0.999976853888107, 0.9947634808233639, 0.9991247361013371, 1.0, 0.9998112024982406, 0.999998460591133, 0.9999977458655877, 0.9719215671182266, 0.9835776411857846, 1.0, 0.9657615675580578, 1.0, 1.0, 0.999976853888107, 0.9883862046973962, 0.9859285934201266, 0.9993997404996481, 0.9916450233110485, 1.0, 0.9992849995601689, 0.9985072132301196, 0.973717067646024, 0.9747045434553132, 0.971659152885292, 0.9757413903061225, 0.9774126935256862, 0.9996711162913441, 0.9812411483990148, 0.9781698077938071, 1.0, 1.0, 0.9859029182793807, 0.9931429231175228, 0.9804628122800845, 0.9999999450211119, 0.9873411110133709, 0.9999992852744546, 0.9918523486980999, 0.9799153325123152, 0.9801156755805771, 0.9901497566006082]
accuracy_cnn = [0.9631535490371698, 0.9638338433597055, 0.9999961126038712, 0.9893434032442653, 0.9787477608598298, 0.975598192516296, 0.9702222346618898, 0.980378912275464, 0.991199557147833, 0.9721998308205205, 0.9711513223366671, 0.9849739699955217, 0.9841852950689157, 0.9815956672637707, 0.9984696098920237, 0.9984529718365925, 0.982502052545156, 0.9786015947653879, 0.9960762178434592, 0.9767463738368911, 0.9786454445937205, 0.9863378240533412, 0.994859929342688, 0.9793720766781112, 0.9730035888441061, 0.9986081566900532, 0.9503416243717968, 0.9999703002935761, 0.9999936246703488, 0.9825384385729213, 0.9702416716425337, 0.9714450539881574, 0.9897049310842414, 0.9707558964024481, 0.9803247997213514, 0.9494175125640643, 0.973370092551127, 0.9538985918296263, 0.9746701933124347, 0.98191925411753, 0.9813961660944419, 0.9750474262327711, 0.99813109543713, 0.975811377319998, 0.9791663556749763, 0.9999998445041548, 1.0, 0.9951866261133503, 0.9691154152361049, 0.9919624197641439, 0.9787874123003434, 0.9848180076628352, 0.978368040005971, 0.9755401925660546, 0.978830329153605, 0.9815889809424292, 0.9810820922543521]
accuracy_transformer = [0.9900756255208278, 0.9825381259163933, 0.9999991429415301, 0.999581261009905, 0.9881828778177445, 0.98703343055453, 0.9796455865444458, 0.9956520434911024, 0.9948906459320049, 0.9665592596597082, 0.983728448275862, 0.9882428719106339, 0.9943064616934421, 0.9989887039693675, 0.9990029772892691, 0.9993163969789348, 0.9846307330618875, 0.9946367588422063, 0.9991032531302413, 0.9925132975917975, 0.9993021566228204, 0.9984973457558465, 0.998802557462474, 0.9775213011993544, 0.9870959298952543, 0.999757650235757, 0.9909481440069198, 0.9999980221727619, 0.9999994396156159, 0.9846307000981003, 0.99224718093691, 0.9913693882448498, 0.9997133798694107, 0.9913619384289195, 0.9923225691184692, 0.9905362614845835, 0.9934140990073944, 0.9525418376388435, 0.9796430153690362, 0.9777863959768357, 0.9812149265303108, 0.9805912516745604, 0.9996671976034008, 0.9854976147403508, 0.9810458223014525, 0.9999987473760825, 1.0, 0.9953691482684782, 0.9829687648337043, 0.9957841953143954, 0.9987138189470576, 0.9887018926488117, 0.9871573084672103, 0.991894204702482, 0.9815836594550691, 0.9775543309142308, 0.9900689303401712]
accuracy_lstm = [0.9912860837438424, 0.9843817118226601, 0.999999815270936, 0.9996802955665025, 0.9725715517241379, 0.9839412561576355, 0.9798122536945812, 0.9942737684729064, 0.9934022167487685, 0.9660660098522168, 0.9801084975369458, 0.9884321428571429, 0.9953070197044335, 0.9994764778325124, 0.9992303571428571, 0.9995977216748768, 0.9846908251231528, 0.9902948891625616, 0.999286330049261, 0.9989394704433497, 0.9995482142857143, 0.9996929802955665, 0.9991039408866995, 0.9816608374384237, 0.9753192118226601, 0.9998235221674877, 0.9775487684729064, 0.9999994458128079, 0.9999996305418719, 0.9846908251231528, 0.989883066502463, 0.9867543103448276, 0.999331157635468, 0.9942300492610837, 0.998979618226601, 0.9745336206896552, 0.9958293103448276, 0.9614072660098523, 0.9786992610837438, 0.9741576354679803, 0.9768926108374384, 0.9778886699507389, 0.9996849753694581, 0.9895104679802955, 0.9776512315270935, 0.9999999384236453, 1.0, 0.9955336206896551, 0.9878097906403941, 0.9976741995073891, 0.9994889778325123, 0.9883799261083743, 0.9869729679802955, 0.9924912561576354, 0.9734576354679803, 0.9727519704433497, 0.989074278676988]
accuracy_rf = [0.9862854064039409, 0.9903962438423646, 1.0, 0.9974181034482759, 0.9929799876847291, 0.9813713054187192, 0.9673035714285714, 1.0, 0.9836560960591133, 0.9790932881773399, 0.9797835591133005, 0.9871154556650247, 0.9862253694581281, 0.9993790024630542, 0.9998540640394089, 0.9984744458128079, 0.9999270320197045, 0.9870791256157635, 0.9991505541871921, 0.9999827586206896, 0.9992638546798029, 0.9999276477832513, 0.9996856527093596, 0.9780431034482758, 0.977696736453202, 0.9999873768472907, 0.9675424876847291, 1.0, 1.0, 0.9999270320197045, 0.9834177955665024, 0.9812481527093596, 0.9994479679802956, 0.9962875615763547, 1.0, 0.9988987068965517, 0.9934861453201971, 0.9686853448275862, 0.976198275862069, 0.9761213054187192, 0.9760298645320197, 0.9758272783251232, 0.9996733374384237, 0.9756536330049261, 0.9743494458128079, 1.0, 1.0, 0.9946964285714286, 0.9910332512315271, 0.9821434729064039, 0.9998291256157635, 0.9869193349753694, 0.9999975369458128, 0.9866779556650246, 0.980435960591133, 0.9805252463054187, 0.98955593552076]
accuracy_nb = [0.9874070433876468, 0.9676943207654415, 0.9999997039598333, 0.996904604016673, 0.9801241592459264, 0.9786854040356195, 0.9716659956422887, 0.9817269207086018, 0.9764535572186435, 0.9749191810344827, 0.97506246447518, 0.9850135586396362, 0.9799169311292156, 0.9890858871731717, 0.9978489721485411, 0.9838255494505495, 0.9892149606858659, 0.9744031830238726, 0.9985351932550208, 0.9951455333459643, 0.9887865905646078, 0.9978856811292156, 0.9957003126184161, 0.9720887410003789, 0.9706769254452444, 0.9991243131868132, 0.973346615668814, 0.9993472314323607, 0.9999772049071618, 0.9892161448465328, 0.9799030172413793, 0.9760539029935582, 0.9970600251042061, 0.9841982640204623, 0.9964386367942403, 0.9533973569533915, 0.9892205854490337, 0.95785957038651, 0.9803790498294809, 0.9792967269799167, 0.9790909790640394, 0.9783286756347102, 0.9996684350132626, 0.9765003315649867, 0.9762599469496022, 0.987196558829102, 0.9809625449981053, 0.978825134994316, 0.9746989271504358, 0.9743451591511937, 0.9944086893709738, 0.9848158038082607, 0.9791063731527093, 0.9815105153467223, 0.9794805679234558, 0.9790998602690413, 0.9833551521984789]
recall_ffnn = [0.319368842364532, 0.5285283251231527, 1.0, 0.992512315270936, 0.8578355911330049, 0.5991933497536945, 0.4986853448275862, 0.999975369458128, 0.15666871921182265, 0.48298029556650246, 0.5875431034482759, 0.6153848522167488, 0.8203694581280788, 0.997823275862069, 0.9999630541871921, 0.9385098522167488, 0.99873460591133, 0.9043411330049261, 0.959371921182266, 1.0, 0.9959759852216749, 0.9999137931034483, 1.0, 0.31430110837438424, 0.7021459359605912, 1.0, 0.39229371921182266, 1.0, 1.0, 0.9999692118226601, 0.656228448275862, 0.6653971674876847, 0.9666871921182266, 0.7855849753694581, 1.0, 0.9730911330049261, 0.9786730295566503, 0.6406681034482758, 0.15382697044334975, 0.23440270935960592, 0.14402401477832513, 0.09804187192118227, 0.9918349753694581, 0.06058497536945813, 0.13044027093596058, 1.0, 1.0, 0.6132204433497537, 0.8582173645320197, 0.7277894088669951, 0.999996921182266, 0.6198245073891626, 0.9999907635467981, 0.7836483990147783, 0.4261915024630542, 0.384064039408867, 0.7241931848170302]
recall_cnn = [0.34420062695924764, 0.2930599094392198, 0.9999912922326716, 0.8613200975269941, 0.017789968652037618, 0.2998084291187739, 0.16024904214559388, 0.44037791710205504, 0.7212121212121212, 0.053657262277951936, 0.3013322884012539, 0.4778909787530477, 0.4082636711947057, 0.721569139672588, 0.9755834204110067, 0.9146638801811215, 0.5482584465343086, 0.641100661790317, 0.856478578892372, 0.5562957157784744, 0.5390282131661442, 0.4713166144200627, 0.8803030303030303, 0.03524033437826541, 0.08347265761058864, 0.9622169975618251, 0.4254266805990944, 0.9992163009404389, 0.9998171368861024, 0.474695228143504, 0.4229275513758272, 0.400095785440613, 0.4902473005921282, 0.3514193660745385, 0.31007488679902473, 0.30039184952978054, 0.7995471960989202, 0.21163357715081854, 0.04027342389411355, 0.0012103796586555207, 0.0040839428770463254, 0.03843608498780913, 0.9543451758969, 0.10159352142110763, 0.04306861720654824, 1.0, 1.0, 0.7560083594566354, 0.10510275165447579, 0.7336468129571578, 0.4396551724137931, 0.5346656217345872, 0.42553117380703587, 0.3890717520027865, 0.016910484151863463, 0.0029432253570184606, 0.47029858312185896]
recall_transformer = [0.771287750129218, 0.493764306283689, 1.0, 0.9892564424425903, 0.6413350070146939, 0.5827309311083216, 0.4059661817913313, 0.7842870855792661, 0.8432197445174628, 0.3496215757217751, 0.605349627113638, 0.7217289374584657, 0.8871372664845307, 0.9865963966624824, 0.9933766521450196, 0.9771081001255261, 0.5644853429816141, 0.9372129513401757, 0.958705604371262, 0.6149062246178838, 0.9869729749686185, 0.946346821236063, 0.9518755076423244, 0.39946651406630734, 0.38455290556006794, 0.9907516798346009, 0.8878756553200916, 1.0, 0.9999944620837333, 0.5748246326515543, 0.7676198035885697, 0.6811932363582662, 0.9885845086022299, 0.929840138817101, 0.9697315956582736, 0.7398416155947722, 0.9517407516798346, 0.705932954293731, 0.07034630436387802, 0.1310621723399542, 0.0767444436240124, 0.0343406187698442, 0.993254817987152, 0.6769862659676585, 0.16459056339068154, 1.0, 1.0, 0.8517075241822344, 0.8710754633389943, 0.9277984936867755, 0.9620597356567969, 0.5625230746511113, 0.7699808018902754, 0.7721165915971351, 0.04628775012921805, 0.5519862659676585, 0.721930049524794]
recall_lstm = [0.7505827586206897, 0.17596551724137932, 1.0, 0.9905310344827586, 0.11656896551724139, 0.5768, 0.46208275862068965, 0.8216551724137932, 0.7854827586206896, 0.2570034482758621, 0.5553793103448276, 0.6499758620689655, 0.8804724137931035, 0.9898689655172414, 0.9913310344827586, 0.9820620689655173, 0.5573620689655172, 0.8644068965517241, 0.9639758620689656, 0.9505034482758621, 0.9893724137931035, 0.990496551724138, 0.9664275862068965, 0.4068551724137931, 0.5777275862068966, 0.9967758620689655, 0.5296620689655173, 1.0, 0.9999931034482759, 0.5853206896551724, 0.7190517241379311, 0.6451241379310345, 0.9626620689655172, 0.9001931034482759, 0.9911620689655173, 0.6037034482758621, 0.9504413793103448, 0.5285551724137931, 0.03135172413793103, 0.09000344827586207, 0.056351724137931034, 0.04573793103448276, 0.9912310344827586, 0.6825413793103449, 0.35002758620689656, 1.0, 1.0, 0.8412172413793103, 0.8304137931034483, 0.9308068965517241, 0.9805482758620689, 0.6463310344827586, 0.6846862068965517, 0.8006689655172414, 0.11392413793103448, 0.12709310344827587, 0.6940798029556651]
recall_rf = [0.8889655172413793, 0.7133103448275863, 1.0, 0.992551724137931, 0.8063965517241379, 0.5184655172413793, 0.3274310344827586, 1.0, 0.14374137931034484, 0.308051724137931, 0.4819827586206897, 0.5870172413793103, 0.668344827586207, 0.9966724137931035, 1.0, 0.9155, 0.9959137931034483, 0.8651896551724138, 0.9524310344827587, 0.9998793103448276, 0.9873448275862069, 0.9960689655172413, 0.9928620689655172, 0.10155172413793104, 0.6692068965517242, 1.0, 0.3433793103448276, 1.0, 1.0, 1.0, 0.5330344827586206, 0.5915344827586206, 0.9703448275862069, 0.8528448275862069, 1.0, 0.9685344827586206, 0.9778103448275862, 0.6536206896551724, 0.1045, 0.11186206896551724, 0.10675862068965518, 0.11486206896551725, 0.983396551724138, 0.16703448275862068, 0.18889655172413794, 1.0, 1.0, 0.755551724137931, 0.7525172413793103, 0.7084310344827586, 0.9906551724137931, 0.5418275862068965, 1.0, 0.6830344827586207, 0.31036206896551727, 0.3040344827586207, 0.7075661945812808]
recall_nb = [0.7311671087533157, 0.602420424403183, 1.0, 0.9386273209549072, 0.013693633952254642, 0.3016246684350133, 0.2675895225464191, 0.4612897877984085, 0.3918269230769231, 0.08852785145888595, 0.4437334217506631, 0.7876989389920425, 0.5568965517241379, 0.7715848806366048, 1.0, 0.5789124668435013, 0.4683189655172414, 0.8220490716180371, 0.9179708222811671, 0.8469164456233422, 0.42337533156498675, 0.9518236074270557, 0.8835212201591512, 0.2802055702917772, 0.46644562334217504, 0.9997015915119364, 0.2610576923076923, 1.0, 1.0, 0.9275696286472148, 0.4100464190981432, 0.5410643236074271, 0.8356100795755969, 0.4422579575596817, 0.9572944297082228, 0.35023209549071616, 0.9506631299734748, 0.4419429708222812, 0.013594164456233421, 0.021170424403183025, 0.0245026525198939, 0.030056366047745357, 0.9839688328912467, 0.17160145888594164, 0.18312334217506632, 0.5, 0.23255968169761274, 0.31147214854111405, 0.5625165782493369, 0.4176889920424403, 0.703564323607427, 0.22244694960212202, 0.8001989389920424, 0.566196949602122, 0.020159151193633953, 0.022397214854111405, 0.5339442615574082]
precision_ffnn = [0.8017111456328688, 0.9474939148576822, 1.0, 0.9952271281883462, 0.8310466191427804, 0.5731982446322859, 0.2176541570811206, 0.9999846057691419, 0.7861998640380693, 0.39683186149639144, 0.540203757540416, 0.6591444975382291, 0.7970398466080578, 0.9981521005996433, 1.0, 0.9361205543732284, 0.9999691737644074, 0.8206903488625505, 0.991333893257998, 1.0, 0.9934678459554082, 1.0, 0.9998737844052936, 0.2617007149760436, 0.5303441491847997, 1.0, 0.2304980191392753, 1.0, 1.0, 0.9987361662479513, 0.6815625129905637, 0.5947455033793453, 0.9996879755984183, 0.7560617868159285, 1.0, 0.9866853976430188, 0.940180066134671, 0.36543192965634236, 0.21240965904259843, 0.22199478647282142, 0.2227645683427543, 0.212684673131896, 0.9897688937501152, 0.3529242965008878, 0.2698552220077835, 1.0, 1.0, 0.6036362313877263, 0.7798920038050473, 0.46964416982893925, 1.0, 0.6534464179065721, 0.9999692124861841, 0.765606670396506, 0.43616914012036423, 0.43561949993015786, 0.7241931848170302]
precision_cnn = [0.19648369346396458, 0.18186386823448036, 0.9997910554312529, 0.6528072016420167, 0.07881944444444444, 0.310322760908165, 0.1621866958085099, 0.4495777402435772, 0.7711444638933374, 0.08079404206220171, 0.24736055812490618, 0.5994320353885643, 0.5814472623550567, 0.48960407447015936, 0.9408938979122227, 0.9985835020772134, 0.5093436018573948, 0.43302631424168636, 0.9182896088133694, 0.3931989536851823, 0.4231284519057254, 0.6659694367202303, 0.8396232683299558, 0.1561764365376452, 0.12298099991019538, 0.9599350203712873, 0.16165332680402478, 0.9991205997335678, 0.9998258431369135, 0.5119454565944179, 0.2796545271340147, 0.28593209369477013, 0.8801275637818909, 0.2621537702021514, 0.429489808225787, 0.12344517126375908, 0.38249089803297537, 0.10555574858413537, 0.08070567295443838, 0.08100233100233101, 0.08170731707317073, 0.08105180043702602, 0.9417734354188686, 0.18214887903578342, 0.1703520011021561, 0.9999912923084961, 1.0, 0.9672998718734332, 0.1118421052631579, 0.7997038555726408, 0.41196484958265, 0.5814598761340177, 0.40051798183785203, 0.33894435004248086, 0.07710326755866122, 0.07975460122699386, 0.47029858312185896]
precision_transformer = [0.7022301102702049, 0.5114642629734231, 0.9999520070291243, 0.9873190575239091, 0.6790718038528897, 0.653586394805711, 0.4265338500149341, 0.9657997449472504, 0.8670075561300314, 0.22241624909135535, 0.539572429203023, 0.6550114089844497, 0.8115698264492258, 0.9580230050710102, 0.9528001558101241, 0.9844938027288824, 0.5703890784218999, 0.7977859662630913, 0.990778047403202, 0.9473682713665308, 0.974282767467965, 0.9687815939906458, 0.9804984160667496, 0.377660344956972, 0.7820348221726693, 0.9956553356633497, 0.6922169132462149, 0.9998892539407139, 0.9999741569155172, 0.5689473722675749, 0.7918524894219088, 0.8054778852429316, 0.9953331214559323, 0.6921482975679936, 0.7081437685941946, 0.7327685030962667, 0.7480521628609483, 0.22998132091107767, 0.25062478625733303, 0.25897204886251307, 0.37353770957249904, 0.22073900042716788, 0.9881691361743078, 0.5805528864038955, 0.421362545131472, 0.9999298579808696, 1.0, 0.8846678183906415, 0.5136360717228527, 0.8498797739547436, 0.9657822367835859, 0.7423693551255472, 0.6115072686436752, 0.7735416720606892, 0.3736180230652323, 0.40559489883254235, 0.721930049524794]
precision_lstm = [0.7588198792408629, 0.7767005068416006, 0.9999896552794282, 0.9915567828788402, 0.15155930562031492, 0.547825688253673, 0.43812631393102003, 0.8523576840252688, 0.8352277727259394, 0.18171644520297453, 0.45348830661283146, 0.6858081557806497, 0.8600448654037887, 0.9809859684375277, 0.9664337027811114, 0.9953482520122043, 0.5733953904168633, 0.6794049332325113, 0.99592797902357, 0.9896989390158519, 0.9853866945080759, 0.9922963720403214, 0.9831064964220569, 0.4839461206542961, 0.3757383975707449, 0.9933641699542262, 0.4022974657684934, 0.9999689664803506, 0.999986206991676, 0.5694029325041009, 0.715722381061888, 0.6251161112262014, 0.9998782261126193, 0.8012375082868859, 0.9535304947834596, 0.3695711830989483, 0.8378056342480577, 0.2382700044146816, 0.12268580989906623, 0.1435051296994755, 0.1385525824939804, 0.1387215528781794, 0.9911285039478674, 0.7165814701112141, 0.3678359182490216, 0.9999965517360285, 1.0, 0.9020596065670758, 0.6181068712478408, 0.9384471507688457, 0.9907392245058655, 0.6851181729792165, 0.6230728919878121, 0.7835656194107921, 0.15950831386029624, 0.16292403037724007, 0.6940798029556651]
precision_rf = [0.5750292756370936, 0.7396177842930439, 1.0, 0.8786056591679131, 0.8016557256226111, 0.4799993615119397, 0.22036435367834764, 1.0, 0.7089888595969045, 0.3914853524397993, 0.4397307032859862, 0.6554684943110718, 0.6031617601294579, 0.9694118830809478, 0.9918938331566166, 0.9989840648693394, 1.0, 0.595062196871776, 1.0, 0.9991557837428069, 0.9718785533662576, 0.9998788487166618, 0.9895691921708797, 0.23469875677398788, 0.42157512300557193, 0.999293602798022, 0.2282531459875765, 1.0, 1.0, 0.9959304222401566, 0.5358894801615504, 0.4796851406520888, 0.998704594254077, 0.93351324828263, 1.0, 0.9697550365114713, 0.7405429403392397, 0.31715887224964445, 0.1928412344893414, 0.19942214298887317, 0.19206551071683364, 0.1968850666430239, 0.9982847641550713, 0.2394878006575532, 0.23199576495500265, 1.0, 1.0, 0.9349690633667591, 0.7471583127910162, 0.5000121690031153, 0.9997737989594753, 0.6638641260720775, 0.9998620879878637, 0.6141825059688072, 0.43327877533336545, 0.4351710182123291, 0.7075661945812808]
precision_nb = [0.626245988697356, 0.29912250374541083, 0.999983422025497, 0.8934229628226977, 0.09750914886081927, 0.378513325150311, 0.2385181463529968, 0.487687319253352, 0.35547768018289017, 0.15221914996721872, 0.3455951658510762, 0.5568199130444973, 0.4496740425417989, 0.6684091855639012, 0.8924925280383511, 0.5442982729596608, 0.866294581250575, 0.3956877014906317, 1.0, 0.8770128755364807, 0.8918767898302717, 0.9312895377128954, 0.87666140281616, 0.24941711182598944, 0.2961590686609897, 0.9535119066443186, 0.2572744947473328, 0.964734106357457, 0.9987251022401775, 0.6357417991341795, 0.4336711435284216, 0.3801985042286992, 0.999702493107757, 0.5747990778048307, 0.8593112890264591, 0.15160169929387451, 0.6316809870015422, 0.19696622655032028, 0.10792313766780731, 0.1049474030243261, 0.11142103279306445, 0.10981223500908541, 0.9974288307061473, 0.26032392736783866, 0.2632256219616814, 0.697357164327499, 0.43778672408950475, 0.3851341655904721, 0.36482200264496223, 0.32835918154567967, 0.9768442858786972, 0.7535238950974336, 0.4519771895161668, 0.4848385906135544, 0.10643326039387309, 0.10407518681149372, 0.5339442615574082]
mcc_ffnn = 0.7198734436749525
mcc_cnn = 0.4618664231472665
mcc_transformer = 0.7179922795829832
mcc_lstm = 0.6890850103646391
mcc_rf = 0.7028231329033506
mcc_nb = 0.5266967369780202
# Cohen's Kappa is not used as these values are almost the same like MCC.
statistics_dict = {
    "FFNN": [f1_ffnn, accuracy_ffnn, recall_ffnn, precision_ffnn, mcc_ffnn],
    "CNN": [f1_cnn, accuracy_cnn, recall_cnn, precision_cnn, mcc_cnn],
    "Transformer": [f1_transformer, accuracy_transformer, recall_transformer, precision_transformer, mcc_transformer],
    "LSTM": [f1_lstm, accuracy_lstm, recall_lstm, precision_lstm, mcc_lstm],
    "RF": [f1_rf, accuracy_rf, recall_rf, precision_rf, mcc_rf],
    "NB": [f1_nb, accuracy_nb, recall_nb, precision_nb, mcc_nb]
}


class EnsembleModel:
    def __init__(self, models, architectures, strategy, cipher_indices):
        self.models = models
        self.architectures = architectures
        self.strategy = strategy
        self.load_model()
        for key in statistics_dict:
            statistics = statistics_dict[key]
            for i in range(4):
                new_list = []
                for index in cipher_indices:
                    new_list.append(statistics[i][index])
                statistics[i] = new_list
        self.total_votes = [0]*len(cipher_indices)
        for key in statistics_dict:
            statistics = statistics_dict[key]
            network_total_votes = [0]*len(cipher_indices)
            for statistic in statistics[:-1]:
                for i in range(len(statistic)):
                    network_total_votes[i] += statistic[i]
            network_total_votes = [total_votes + statistics[-1] for total_votes in network_total_votes]
            statistics.append(network_total_votes)
            for i in range(len(network_total_votes)):
                self.total_votes[i] += network_total_votes[i]

    def load_model(self):
        for j in range(len(self.models)):
            if self.architectures[j] in ("FFNN", "CNN", "LSTM", "Transformer"):
                if self.architectures[j] == 'Transformer':
                    model_ = tf.keras.models.load_model(self.models[j], custom_objects={
                        'TokenAndPositionEmbedding': TokenAndPositionEmbedding, 'MultiHeadSelfAttention': MultiHeadSelfAttention,
                        'TransformerBlock': TransformerBlock})
                else:
                    model_ = tf.keras.models.load_model(self.models[j])
                optimizer = Adam(learning_rate=config.learning_rate, beta_1=config.beta_1, beta_2=config.beta_2, epsilon=config.epsilon,
                                 amsgrad=config.amsgrad)
                model_.compile(optimizer=optimizer, loss="sparse_categorical_crossentropy",
                               metrics=["accuracy", SparseTopKCategoricalAccuracy(k=3, name="k3_accuracy")])
                self.models[j] = model_
            else:
                with open(self.models[j], "rb") as f:
                    self.models[j] = pickle.load(f)

    def evaluate(self, batch, batch_ciphertexts, labels, batch_size, verbose=0):
        correct_all = 0
        prediction = self.predict(batch, batch_ciphertexts, batch_size, verbose=0)
        for i in range(0, len(prediction)):
            if labels[i] == np.argmax(prediction[i]):
                correct_all += 1
        if verbose == 1:
            print("Accuracy: %f" % (correct_all / len(prediction)))
        return correct_all / len(prediction)

    def predict(self, batch, ciphertexts, batch_size, verbose=0):
        results = []
        for i in range(len(self.models)):
            if self.architectures[i] == "FFNN":
                results.append(self.models[i].predict(batch, batch_size=batch_size, verbose=verbose))
            elif self.architectures[i] in ("CNN", "LSTM", "Transformer"):
                input_length = get_model_input_length(self.models[i], self.architectures[i])
                if isinstance(ciphertexts, list):
                    split_ciphertexts = []
                    for ciphertext in ciphertexts:
                        if len(ciphertext) < input_length:
                            ciphertext = pad_sequences([ciphertext], maxlen=input_length, padding='post', value=len(OUTPUT_ALPHABET))[0]
                        split_ciphertexts.append([ciphertext[input_length*j:input_length*(j+1)] for j in range(
                            len(ciphertext) // input_length)])
                    split_results = []
                    if self.architectures[i] in ("LSTM", "Transformer"):
                        for split_ciphertext in split_ciphertexts:
                            for ct in split_ciphertext:
                                split_results.append(self.models[i].predict(tf.convert_to_tensor([ct]), batch_size=batch_size, verbose=verbose))
                    elif self.architectures[i] == "CNN":
                        for split_ciphertext in split_ciphertexts:
                            for ct in split_ciphertext:
                                split_results.append(self.models[i].predict(tf.reshape(tf.convert_to_tensor([ct]), (1, input_length, 1)),
                                                     batch_size=batch_size, verbose=0))
                    res = split_results[0]
                    for split_result in split_results[1:]:
                        res = np.add(res, split_result)
                    for j in range(len(res)):
                        res[j] /= len(split_results)
                    results.append(res)
                else:
                    if self.architectures[i] in ("LSTM", "Transformer"):
                        res = self.models[i].predict(ciphertexts, batch_size=batch_size, verbose=verbose)
                    elif self.architectures[i] == "CNN":
                        res = self.models[i].predict(tf.reshape(
                            ciphertexts, (len(ciphertexts), input_length, 1)), batch_size=batch_size, verbose=verbose)
                    results.append(res)
            elif self.architectures[i] in ("DT", "NB", "RF", "ET"):
                results.append(self.models[i].predict_proba(batch))
        res = [[0.] * len(results[0][0]) for _ in range(len(results[0]))]
        if self.strategy == 'mean':
            for result in results:
                for i in range(len(result)):
                    for j in range(len(result[i])):
                        res[i][j] += result[i][j]
            for i in range(len(results[0])):
                for j in range(len(results[0][0])):
                    res[i][j] = res[i][j] / len(results)
        elif self.strategy == 'weighted':
            for i in range(len(results)):
                statistics = statistics_dict[self.architectures[i]]
                for j in range(len(results[i])):
                    for k in range(len(results[i][j])):
                        res[j][k] += results[i][j][k] * statistics[-1][k] / self.total_votes[k]
            for i in range(len(results[0])):
                for j in range(len(results[0][i])):
                    res[i][j] = res[i][j] / len(results)
        else:
            raise ValueError("Unknown strategy %s" % self.strategy)
        return res
