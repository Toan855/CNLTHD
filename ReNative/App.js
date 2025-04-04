import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import Home from "./components/Home/Home";

const Tab = createBottomTabNavigator()
const TabNavigator=()=>{
  return(
    <Tab.Navigator>
      <Tab.Screen name="Index"component={Home}></Tab.Screen>
    </Tab.Navigator>
  )
}