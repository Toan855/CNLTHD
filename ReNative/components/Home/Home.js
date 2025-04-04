import { useEffect, useState } from "react";
import { View, Text, FlatList, Image, TouchableOpacity} from "react-native";
import MyStyles from "../../styles/MyStyles";
import Apis, { endpoints } from "../../configs/Apis";
import { ActivityIndicator, Chip, List, Searchbar } from "react-native-paper";
import { SafeAreaView } from "react-native-safe-area-context";
const Home=()=>{
    const[categories, setcategories]=useState([]);
    const loadCates=async()=>{
        let res=await Apis.get(endpoints['categories'])
        setcategories(res.data)
    }
    const [loading, setLoading] = useState(false);
    const[courses,setCourses]=useState([]);
    const [kw, setKw] = useState("");
    const [cateId, setCateId] = useState(null);
    const [page, setPage] = useState(1);
    const loadCourses=async()=>{
       if (page>0) {
        try {
            setLoading(true)
            let url = `${endpoints['courses']}?page=${page}`;
            if (kw) {
                url = `${url}&q=${kw}`;
            }
            if (cateId) {
                url = `${url}&category_id=${cateId}`;
            }    
            let res=await Apis.get(url)
            setCourses([...courses,...res.data.results])
            if (res.data.next === null)
                setPage(0);
           } catch (error) {
            
           }finally{
                setLoading(false)
           }
       }
    }
    useEffect(()=>{
        loadCates()
    },[])
    useEffect(() => {
        let timer = setTimeout(() => {
            loadCourses();
        }, 500);

        return () => clearTimeout(timer);
    }, [kw, page, cateId]);
    const search = (value, callback) => {
        setPage(1);
        setCourses([]);
        callback(value);
    }
    const loadMore = () => {
        if (!loading && page > 0)
            setPage(page + 1);
    }
    return(
        
        <SafeAreaView style={MyStyles.container}>
            
            <View style={[MyStyles.wrap,MyStyles.row]}>
            <TouchableOpacity onPress={() => search(null, setCateId)}>
                <Chip style={MyStyles.m}  icon="label">Tất cả</Chip>
            </TouchableOpacity>
            {categories.map(c => <TouchableOpacity key={c.id} onPress={() => search(c.id, setCateId)}>
                <Chip style={MyStyles.m}  icon="google-downasaur">{c.name}</Chip>
            </TouchableOpacity>)}
            </View>
            <Searchbar placeholder="Tìm kiếm khóa học.." onChangeText={t => search(t, setKw)} value={kw} />
            <FlatList ListFooterComponent={loading && <ActivityIndicator />}onEndReached={loadMore} data={courses}  renderItem={({item}) => <List.Item key={item.id} title={item.subject} description={item.created_date} 
                                                   left={() => <Image style={MyStyles.avatar} source={{uri: item.image}} />} />} />
        </SafeAreaView>
        

    )
};
export default Home