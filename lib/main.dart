import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

void main() => runApp(RealApp());

class RealApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Real Satisfaction v2.2',
      theme: ThemeData.dark().copyWith(scaffoldBackgroundColor: Color(0xFF0A0A0A)),
      home: Cockpit(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class Cockpit extends StatefulWidget { @override _CockpitState createState() => _CockpitState(); }

class _CockpitState extends State<Cockpit> {
  Map<String,String> dict = {};
  TextEditingController nenoCtrl = TextEditingController();
  TextEditingController maanaCtrl = TextEditingController();
  String log = "Replica inangoja funzo lako...";

  @override
  void initState(){ super.initState(); loadDict(); }

  loadDict() async {
    var p = await SharedPreferences.getInstance();
    var s = p.getString('rs_dict');
    if(s!=null){ setState(()=> dict = Map<String,String>.from(jsonDecode(s))); }
  }

  funza() async {
    var n = nenoCtrl.text.trim().toLowerCase();
    var m = maanaCtrl.text.trim();
    if(n.isEmpty||m.isEmpty) return;
    dict[n]=m;
    var p = await SharedPreferences.getInstance();
    await p.setString('rs_dict', jsonEncode(dict));
    setState(()=> log = "✅ LOCKED: $n = $m (taught by Mkuu)");
    nenoCtrl.clear(); maanaCtrl.clear();
  }

  @override
  Widget build(BuildContext context){
    return Scaffold(
      appBar: AppBar(title: Text("Real Satisfaction 🟢 v2.2"), backgroundColor: Color(0xFF111111)),
      body: SingleChildScrollView(padding: EdgeInsets.all(16), child: Column(children:[
        Container(padding: EdgeInsets.all(16), decoration: BoxDecoration(color: Color(0xFF1A1A1A), borderRadius: BorderRadius.circular(16)), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children:[
          Text("🟢 Fearless + Peace ON", style: TextStyle(color: Color(0xFF00FF88), fontWeight: FontWeight.bold)),
          Text("✅ Mchana mwema LOCKED (taught by Mkuu)"),
          Text("✅ bunda = Makalio - NO hallucination"),
          Text("✅ Anti-hate ON"),
        ])),
        SizedBox(height:12),
        Container(padding: EdgeInsets.all(16), decoration: BoxDecoration(color: Color(0xFF1A1A1A), borderRadius: BorderRadius.circular(16)), child: Column(children:[
          Text("🧠 FUNZA REPLICA", style: TextStyle(fontWeight: FontWeight.bold)),
          TextField(controller: nenoCtrl, decoration: InputDecoration(hintText: "Neno: e.g. bunda", filled:true, fillColor: Colors.white, hintStyle: TextStyle(color: Colors.black54))),
          SizedBox(height:8),
          TextField(controller: maanaCtrl, decoration: InputDecoration(hintText: "Maana: e.g. makalio", filled:true, fillColor: Colors.white, hintStyle: TextStyle(color: Colors.black54))),
          SizedBox(height:8),
          SizedBox(width: double.infinity, child: ElevatedButton(style: ElevatedButton.styleFrom(backgroundColor: Color(0xFF00FF88)), onPressed: funza, child: Text("FUNZA REPLICA", style: TextStyle(color: Colors.black)))),
          SizedBox(height:8),
          Text(log, style: TextStyle(color: Color(0xFF00FF88))),
        ])),
        SizedBox(height:12),
        SizedBox(width: double.infinity, child: ElevatedButton(style: ElevatedButton.styleFrom(backgroundColor: Color(0xFF00FF88)), onPressed: (){}, child: Text("START AUTOPILOT", style: TextStyle(color: Colors.black)))),
      ])),
    );
  }
}
