import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'package:flutter/services.dart';

void main() => runApp(MaterialApp(home: SmartTeach(), debugShowCheckedModeBanner: false, theme: ThemeData.dark()));

class Msg { String role; String text; Msg(this.role,this.text); }

class SmartTeach extends StatefulWidget { @override _SmartTeachState createState() => _SmartTeachState(); }

class _SmartTeachState extends State<SmartTeach> {
  List<Msg> chats = [];
  Map<String,String> dict = {};
  TextEditingController ctrl = TextEditingController();

  @override
  void initState(){ super.initState(); loadAll(); }

  loadAll() async {
    final p = await SharedPreferences.getInstance();
    String? d = p.getString('dict_smart_v3');
    if(d!=null) dict = Map<String,String>.from(json.decode(d));
    setState(()=> chats.add(Msg("ai","Mulembe! Niko hapa. Nifundishe kama unavyoongea na Meta AI — andika tu: 'Mulembe inamaanisha...' Nitaelewa na kuhifadhi. Maneno sasa: ${dict.length}")));
  }

  saveDict() async {
    final p = await SharedPreferences.getInstance();
    await p.setString('dict_smart_v3', json.encode(dict));
  }

  void assimilate(String t){
    if(t.trim().isEmpty) return;
    setState(()=> chats.add(Msg("user",t)));
    // SMART PARSE: If user wrote "X means Y" or "X inamaanisha Y"
    String lower = t.toLowerCase();
    String word = "";
    String meaning = "";
    if(lower.contains("means")){
      var parts = t.split(RegExp(r'means', caseSensitive:false));
      if(parts.length>=2){ word=parts[0].trim(); meaning=parts[1].trim(); }
    } else if(lower.contains("inamaanisha")){
      var parts = t.split(RegExp(r'inamaanisha', caseSensitive:false));
      if(parts.length>=2){ word=parts[0].trim(); meaning=parts[1].trim(); }
    } else if(lower.contains("=")){
      var parts = t.split("=");
      if(parts.length>=2){ word=parts[0].trim(); meaning=parts[1].trim(); }
    }
    if(word.isNotEmpty && meaning.isNotEmpty){
      dict[word]=meaning;
      saveDict();
      setState(()=> chats.add(Msg("ai","✅ Nimeelewa! Nimehifadhi: $word = $meaning. Maneno: ${dict.length}")));
    } else {
      dict["note_${DateTime.now().millisecondsSinceEpoch}"]=t;
      saveDict();
      setState(()=> chats.add(Msg("ai","👍 Nimepokea note yako. Nimehifadhi kama funzo. Kama ni neno, andika 'neno means maana' ni-assimilate haraka. Maneno: ${dict.length}")));
    }
    ctrl.clear();
  }

  void exportDict(){
    String j = json.encode(dict);
    Clipboard.setData(ClipboardData(text:j));
    showDialog(context: context, builder: (ctx)=> AlertDialog(title: Text("dict.json - COPIED"), content: SingleChildScrollView(child: Text(j)), actions: [TextButton(onPressed: ()=>Navigator.pop(ctx), child: Text("Sawa"))]));
    setState(()=> chats.add(Msg("ai","📤 EXPORTED! ${dict.length} maneno copied. Nenda GitHub > dict.json > Paste > Commit.")));
  }

  @override
  Widget build(BuildContext context){
    return Scaffold(
      appBar: AppBar(title: Text("REAL v3.0 Smart Teach - Track Locked"), backgroundColor: Colors.green[800]),
      body: Column(children: [
        Container(padding: EdgeInsets.all(8), color: Colors.grey[900], width: double.infinity, child: Text("Track: FB Page Reply | Maneno: ${dict.length} | Router: Sheng<>Maragoli", style: TextStyle(color: Colors.green))),
        Expanded(child: ListView.builder(itemCount: chats.length, itemBuilder: (c,i){ bool u=chats[i].role=="user"; return Align(alignment: u? Alignment.centerRight:Alignment.centerLeft, child: Container(margin: EdgeInsets.all(6), padding: EdgeInsets.all(12), decoration: BoxDecoration(color: u? Colors.green[700]:Colors.grey[800], borderRadius: BorderRadius.circular(12)), child: Text(chats[i].text))); })),
        Padding(padding: EdgeInsets.all(8), child: Column(children: [
          Row(children: [Expanded(child: TextField(controller: ctrl, decoration: InputDecoration(hintText: "Andika kama unavyonifundisha mimi... ex: Mulembe means...", border: OutlineInputBorder()))), IconButton(icon: Icon(Icons.send, color: Colors.green), onPressed: ()=>assimilate(ctrl.text))]),
          SizedBox(height:6),
          ElevatedButton(onPressed: exportDict, child: Text("📤 EXPORT TO AI (dict.json)"), style: ElevatedButton.styleFrom(backgroundColor: Colors.orange, minimumSize: Size(double.infinity,45)))
        ]))
      ]),
    );
  }
}
